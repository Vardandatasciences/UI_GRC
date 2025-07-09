# S3 Integration Guide for TaskView.vue

## Overview

This guide explains how the TaskView.vue component has been integrated with the S3 upload functionality from `s3_functions.py`. The integration allows audit evidence files to be uploaded directly to Amazon S3 through the Render microservice.

## Changes Made

### 1. Backend Changes

#### New Endpoint: `upload_evidence_to_s3`
- **File**: `backend/grc/auditing.py`
- **Purpose**: Handles file uploads to S3 using the RenderS3Client
- **Features**:
  - File validation (size, type)
  - Temporary file handling
  - S3 upload via Render microservice
  - Progress tracking
  - Error handling with CORS support

#### URL Configuration
- **File**: `backend/grc/urls.py`
- **Added**: `path('upload-evidence-s3/', upload_evidence_to_s3, name='upload_evidence_to_s3')`

### 2. Frontend Changes

#### TaskView.vue Updates
- **File**: `frontend/src/components/Auditor/TaskView.vue`
- **Modified Functions**:
  - `handleComplianceFileUpload()`: Now uses S3 upload endpoint
  - `handleAuditFileUpload()`: Now uses S3 upload endpoint

#### API Service Updates
- **File**: `frontend/src/data/api.js`
- **Fixed**: URL paths for `saveVersion` and `sendForReview` endpoints

## How It Works

### Upload Process Flow

1. **User selects files** in TaskView.vue
2. **Frontend validation** checks file requirements
3. **FormData creation** with file and metadata
4. **S3 upload request** sent to `/api/upload-evidence-s3/`
5. **Backend processing**:
   - Validates file size and type
   - Creates temporary file
   - Initializes S3 client
   - Tests S3 connection
   - Uploads to S3 via Render microservice
   - Cleans up temporary files
6. **Response handling** updates UI with file information

### File Validation

#### Backend Validation
- **Max file size**: 50MB
- **Allowed extensions**: `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.txt`, `.jpg`, `.jpeg`, `.png`, `.gif`, `.zip`, `.rar`
- **Security checks**: File type validation based on extension

#### Generated File Names
Files are stored with unique names to prevent conflicts:
```
{document_type}_{audit_id}_{compliance_id}_{timestamp}_{original_filename}
```

Example: `evidence_123_456_20240115_103000_report.pdf`

## API Endpoints

### Upload Evidence to S3
- **URL**: `POST /api/upload-evidence-s3/`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: The file to upload
  - `userId`: User identifier
  - `documentType`: Type of document ('evidence' or 'audit_evidence')
  - `audit_id`: Audit ID
  - `compliance_id`: Compliance ID (optional for audit evidence)
  - `fileName`: Original filename

### Response Format
```json
{
  "success": true,
  "file": {
    "name": "original_filename.pdf",
    "storedName": "evidence_123_456_20240115_103000_original_filename.pdf",
    "url": "https://s3.amazonaws.com/bucket/path/to/file",
    "s3Key": "path/to/file",
    "size": 1048576,
    "contentType": "application/pdf",
    "uploadedAt": "2024-01-15T10:30:00.000Z",
    "documentType": "evidence",
    "auditId": "123",
    "complianceId": "456"
  },
  "operation_id": 789,
  "message": "File uploaded successfully to S3"
}
```

## Error Handling

### Common Error Scenarios
1. **File too large**: Returns 400 with size limit message
2. **Invalid file type**: Returns 400 with allowed types list
3. **S3 service unavailable**: Returns 503 with retry message
4. **Upload failure**: Returns 500 with error details

### Frontend Error Handling
- Progress indicators show upload status
- Error messages displayed to user
- Retry mechanisms for failed uploads
- Cleanup of temporary UI states

## Configuration Requirements

### Environment Variables
The S3 client uses these environment variables (with defaults):
- `DB_HOST`: MySQL host (default: 'localhost')
- `DB_USER`: MySQL user (default: 'root')
- `DB_PASSWORD`: MySQL password (default: 'root')
- `DB_NAME`: MySQL database (default: 'grc')
- `DB_PORT`: MySQL port (default: 3306)

### Dependencies
- `mysql-connector-python`: For database operations
- `requests`: For HTTP requests to Render microservice
- `tempfile`: For temporary file handling

## Testing

### Test Script
Run the test script to verify integration:
```bash
cd backend
python test_s3_integration.py
```

### Test Coverage
- S3 client creation and connection
- File upload and download
- MySQL operation tracking
- Backend endpoint configuration
- Error handling scenarios

## Usage Examples

### Compliance Evidence Upload
```javascript
// In TaskView.vue
async handleComplianceFileUpload(event) {
  const files = Array.from(event.target.files);
  
  for (let file of files) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('userId', 'current-user');
    formData.append('documentType', 'evidence');
    formData.append('compliance_id', this.selectedCompliance.id);
    formData.append('audit_id', this.$route.params.auditId);
    
    const response = await fetch('/api/upload-evidence-s3/', {
      method: 'POST',
      body: formData,
      credentials: 'include'
    });
    
    const result = await response.json();
    // Handle response...
  }
}
```

### Audit Evidence Upload
```javascript
// Similar to compliance upload but with 'audit_evidence' type
formData.append('documentType', 'audit_evidence');
// No compliance_id needed for audit evidence
```

## Security Considerations

### File Security
- File type validation prevents malicious uploads
- Size limits prevent DoS attacks
- Temporary file cleanup prevents disk space issues
- S3 URLs are generated server-side

### Authentication
- Session-based authentication required
- CORS headers properly configured
- User ID validation on server side

## Troubleshooting

### Common Issues

1. **"S3 service is currently unavailable"**
   - Check Render microservice status
   - Verify network connectivity
   - Wait for service to wake up (cold start)

2. **"MySQL connection failed"**
   - Verify MySQL is running
   - Check database credentials
   - Ensure database exists

3. **"File type not allowed"**
   - Check file extension
   - Verify file isn't corrupted
   - Ensure proper Content-Type header

### Debug Steps
1. Check browser console for frontend errors
2. Review Django logs for backend errors
3. Test S3 connection using test script
4. Verify URL patterns in Django URLs
5. Check file permissions and disk space

## Monitoring

### Operation Tracking
All file operations are tracked in MySQL:
- Upload attempts and results
- File metadata and locations
- User and timestamp information
- Success/failure statistics

### Performance Metrics
- Upload success rate
- Average upload time
- File size distribution
- Error frequency by type

## Future Enhancements

### Potential Improvements
1. **Progress indicators**: Real-time upload progress
2. **Batch uploads**: Multiple file upload optimization
3. **File previews**: Preview uploaded files
4. **Virus scanning**: Integrate antivirus scanning
5. **Compression**: Automatic file compression
6. **Versioning**: File version management

### Scalability Considerations
- Implement file upload queues for high volume
- Add CDN for faster file delivery
- Consider chunked uploads for large files
- Implement file deduplication

## Support

For issues or questions:
1. Check the troubleshooting section
2. Run the test script to verify configuration
3. Review Django and browser logs
4. Consult the S3 microservice documentation

## Summary

The S3 integration provides a robust, scalable solution for audit evidence file uploads. The integration maintains backward compatibility while adding modern cloud storage capabilities with proper error handling and monitoring. 