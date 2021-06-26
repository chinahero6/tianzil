from aiohttp import web
from aiohttp.web_request import Request
from .config import db_block, web_routes, render_html
import psycopg2.errors
from urllib.parse import urlencode
from .config import db_block, web_routes



@web_routes.get("/courses")
async def view_list_courses(request):

    with db_block() as db:
        db.execute("""
        SELECT sn AS stu_sn,no as stu_no, name as stu_name FROM student ORDER BY name
        """)
        students = list(db)
        
        db.execute("""
        SELECT sn AS cou_sn, no as cou_no ,name as cou_name FROM course ORDER BY name
        """)
        courses = list(db)
        db.execute("""
        SELECT g.stu_sn, g.cou_sn, 
            s.name as stu_name, 
            c.name as cou_name, 
            g.grade 
        FROM course_grade as g
            INNER JOIN student as s ON g.stu_sn = s.sn
            INNER JOIN course as c  ON g.cou_sn = c.sn
        ORDER BY stu_sn, cou_sn;
        """)
        items = list(db)

    return render_html(request, 'courses_list.html',
                       students=students,
                       courses=courses,
                       items=items)

@web_routes.post('/course/add')
async def action_grade_add(request):
    params = await request.post()
    cou_sn = params.get("sn")
    cou_name = params.get("name")
    a = params.get("a")
    b = params.get("b")
    c = params.get("c")
    if a is None or cou_sn is None or cou_name is None:
        return web.HTTPBadRequest(text="cou_sn, cou_no, cou_name must be required   数据为空")
    try:
        cou_sn=int(cou_sn)
        cou_name = str(cou_name)
        time='S'+str(a)+'0'+str(b)
    except ValueError:
        return web.HTTPBadRequest(text="invalid value   错误的信息")
    try:
        with db_block() as db:
            db.execute("""
            INSERT INTO course (sn, no, name)  
            VALUES ( %(cou_sn)s, %(time)s, %(cou_name)s)
            """, dict(cou_sn=cou_sn,cou_name = cou_name,time=time))
    except psycopg2.errors.UniqueViolation:
        query = urlencode({
            "message": "已经添加该学生",
            "return": "/course"
        })
        return web.HTTPFound(location=f"/error?{query}")
    except psycopg2.errors.ForeignKeyViolation as ex:
        return web.HTTPBadRequest(text=f"无此学生或课程: {ex}")

    return web.HTTPFound(location="/courses")

# @web_routes.get('/course/edit/{cou_sn}/{cou_no}/{cou_name}')
# def view_course_editor(request):
#     cou_sn = request.match_info.get("cou_sn")
#     cou_no = request.match_info.get("cou_no")
#     cou_name = request.match_info.get("cou_name")
#     if cou_sn is None or cou_no is None or cou_name is None:
#         return web.HTTPBadRequest(text="cou_sn,cou_no,cou_name  must be required")
#     with db_block() as db:
#         db.execute("""
#         SELECT* 
#         FROM student
#         WHERE sn = %(cou_sn)s ;
#         """, dict(cou_sn=cou_sn))
#         record = db.fetch_first()

#     if record is None:
#         return web.HTTPNotFound(text=f"no such course: cou_sn={cou_sn}")

#     return render_html(request, "courses_edit.html",
#                        cou_sn=cou_sn,
#                        cou_no=cou_no,
#                        cou_name=cou_name)

# @web_routes.post('/views/courses/edit/{cou_sn}/{cou_no}/{cou_name}')
# async def edit_grade_action(request):
#     params = await request.post()
#     sn = params.get("sn")
#     name = params.get("name")
#     a = params.get("a")
#     b = params.get("b")
#     if stu_sn is None or stu_no is None or stu_name is None:
#         return web.HTTPBadRequest(text="stu_sn, stu_no,  stu_name must be required")
#     try:
#         sn = int(sn)
#         no = str(no)
#         name = str(name)
#     except ValueError:
#         return web.HTTPBadRequest(text="invalid value")

#     with db_block() as db:
#         db.execute("""
#         UPDATE student SET sn=%(stu_sn)s
#         WHERE no = %(no)s AND cou_sn = %(sn)s
#         """, dict(sn=sn, no=no, name=name))

#     return web.HTTPFound(location="/courses")

@web_routes.get("/courses/delete/{cou_sn}/{cou_no}/{cou_name}")
def courses_deletion_dialog(request):
    cou_sn = request.match_info.get("cou_sn")
    cou_no = request.match_info.get("cou_no")
    cou_name = request.match_info.get("cou_name")
    if cou_sn is None or cou_no is None or cou_name is None:
        return web.HTTPBadRequest(text="cou_sn, cou_no, cou_name must be required")

    with db_block() as db:
        db.execute("""
        SELECT * 
        FROM course
        WHERE sn = %(cou_sn)s;
        """, dict(cou_sn=cou_sn))
        record = db.fetch_first()

    if record is None:
        return web.HTTPNotFound(text=f"no such courses: cou_sn={cou_sn}")

    return render_html(request, 'courses_dialog_deletion.html',
                        record=record,
                        cou_sn=cou_sn,
                       cou_no=cou_no,
                       cou_name=cou_name)



@web_routes.post('/views/courses/delete/{cou_sn}/{cou_no}/{cou_name}')
def delete_courses_action(request):
    cou_sn = request.match_info.get("cou_sn")
    if cou_sn is None:
        return web.HTTPBadRequest(text="cou_sn must be required")
    cou_sn=int(cou_sn)
    try:    
        with db_block() as db:
            db.execute("""
            DELETE FROM course
                WHERE sn = %(cou_sn)s
            """, dict(cou_sn=cou_sn))
    except psycopg2.errors.UniqueViolation:
        query = urlencode({
            "message": "已经添加该学生",
            "return": "/courses"
        })
    except psycopg2.errors.ForeignKeyViolation as ex:
        return web.HTTPBadRequest(text=f"此课程已有学生或成绩: {ex}")

    return web.HTTPFound(location="/courses")
