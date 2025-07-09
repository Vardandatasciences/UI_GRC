from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection
from ..models import Users, Department, BusinessUnit, Entity, Location

@require_http_methods(["GET"])
def get_user_business_info(request, user_id):
    try:
        # Get user's department ID
        user = Users.objects.get(UserId=user_id)
        department_id = user.Department

        # Get department info with related data using raw SQL for efficient joins
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    d.DepartmentName,
                    d.DepartmentHead,
                    bu.Name as BusinessUnitName,
                    e.EntityName,
                    CONCAT(l.AddressLine, ', ', l.City, ', ', l.State, ', ', l.Country) as Location
                FROM department d
                LEFT JOIN businessunits bu ON d.BusinessUnitId = bu.BusinessUnitId
                LEFT JOIN mainentities e ON d.EntityId = e.Id
                LEFT JOIN locations l ON e.LocationId = l.LocationID
                WHERE d.DepartmentId = %s
            """, [department_id])
            
            columns = [col[0] for col in cursor.description]
            result = dict(zip(columns, cursor.fetchone()))

            # Get department head name
            if result['DepartmentHead']:
                dept_head = Users.objects.filter(UserId=result['DepartmentHead']).first()
                if dept_head:
                    result['DepartmentHead'] = f"{dept_head.FirstName} {dept_head.LastName}"

        return JsonResponse({
            'status': 'success',
            'data': result
        })

    except Users.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_user_profile(request, user_id):
    try:
        user = Users.objects.get(UserId=user_id)
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'firstName': user.FirstName,
                'lastName': user.LastName,
                'email': user.Email,
                'username': user.UserName,
                'isActive': user.IsActive,
                'department': user.Department
            }
        })

    except Users.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500) 