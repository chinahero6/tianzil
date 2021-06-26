from aiohttp import web
from aiohttp.web_request import Request
from .config import db_block, web_routes, render_html
import psycopg2.errors
from urllib.parse import urlencode
from .config import db_block, web_routes



@web_routes.get("/select")
async def view_student_list(request):
    with db_block() as db:
        db.execute("""
        SELECT sn AS stu_sn,no as stu_no, name as stu_name FROM student ORDER BY name
        """)
        students = list(db)

        db.execute("""
        SELECT sn AS cou_sn, name as cou_name FROM course ORDER BY name
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

    return render_html(request, 'select_list.html',
                       students=students,
                       courses=courses,
                       items=items)

@web_routes.post('/action/select/add')
async def action_select_add(request):
    params = await request.post()
    stu_sn = params.get("stu_sn")
    cou_sn = params.get("cou_sn")
    t = params.get("t")
    if stu_sn is None or cou_sn is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn must be required")

    try:
        stu_sn = int(stu_sn)
        cou_sn = int(cou_sn)
        grade = -int(t)

    except ValueError:
        return web.HTTPBadRequest(text="invalid value")

    try:
        with db_block() as db:
            db.execute("""
            INSERT INTO course_grade (stu_sn, cou_sn, grade) 
            VALUES ( %(stu_sn)s, %(cou_sn)s, %(grade)s)
            """, dict(stu_sn=stu_sn, cou_sn=cou_sn, grade=grade))
    except psycopg2.errors.UniqueViolation:
        query = urlencode({
            "message": "已经添加该学生的课程",
            "return": "/select"
        })
        return web.HTTPFound(location=f"/error?{query}")
    except psycopg2.errors.ForeignKeyViolation as ex:
        return web.HTTPBadRequest(text=f"无此学生或课程: {ex}")

    return web.HTTPFound(location="/select")

@web_routes.get("/select/delete/{stu_sn}/{cou_sn}")
def select_deletion_dialog(request):
    stu_sn = request.match_info.get("stu_sn")
    cou_sn = request.match_info.get("cou_sn")
    if stu_sn is None or cou_sn is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn, must be required")

    with db_block() as db:
        db.execute("""
        SELECT g.stu_sn, g.cou_sn,
            s.name as stu_name, 
            c.name as cou_name, 
            g.grade 
        FROM course_grade as g
            INNER JOIN student as s ON g.stu_sn = s.sn
            INNER JOIN course as c  ON g.cou_sn = c.sn
        WHERE stu_sn = %(stu_sn)s AND cou_sn = %(cou_sn)s;
        """, dict(stu_sn=stu_sn, cou_sn=cou_sn))

        record = db.fetch_first()

    if record is None:
        return web.HTTPNotFound(text=f"no such grade: stu_sn={stu_sn}, cou_sn={cou_sn}")

    return render_html(request, 'select_dialog_deletion.html', record=record)

@web_routes.post('/action/select/delete/{stu_sn}/{cou_sn}')
def delete_select_action(request):
    stu_sn = request.match_info.get("stu_sn")
    cou_sn = request.match_info.get("cou_sn")
    if stu_sn is None or cou_sn is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn, must be required")

    with db_block() as db:
        db.execute("""
        DELETE FROM course_grade
            WHERE stu_sn = %(stu_sn)s AND cou_sn = %(cou_sn)s
        """, dict(stu_sn=stu_sn, cou_sn=cou_sn))

    return web.HTTPFound(location="/select")

@web_routes.get("/student/select/{user}")
async def view_student_list(request):
    user = request.match_info.get("user")
    with db_block() as db:
        db.execute("""
            SELECT *
            FROM student
            WHERE no=%(user)s;
            """,dict(user=user))
        try:
            students = list(db)
            for x in students:
                b=x.sn
         
        except :
            b
            return web.HTTPFound(location="/student/select/{user}")
            
        db.execute("""
        SELECT sn AS cou_sn, no as cou_no ,name as cou_name FROM course ORDER BY name
        """)
        courses = list(db)
        db.execute("""
        SELECT g.stu_sn, g.cou_sn,
            s.no as stu_no,
            s.name as stu_name, 
            c.name as cou_name,
            c.no as cou_no, 
            g.grade 
        FROM course_grade as g
            INNER JOIN student as s ON g.stu_sn = s.sn
            INNER JOIN course as c ON g.cou_sn = c.sn
        WHERE stu_sn=%(c)s;
        """,dict(c=b))
        items = list(db)
        db.execute("""
            SELECT g.stu_sn, g.cou_sn, 
                s.name as stu_name, 
                c.name as cou_name, 
                g.grade 
            FROM course_grade as g
                INNER JOIN student as s ON g.stu_sn = s.sn
                INNER JOIN course as c  ON g.cou_sn = c.sn
            WHERE grade != -1;
            """)
        grades = list(db)
    return render_html(request, 'student_select.html',
                       students=students,
                       items=items,grades=grades,courses=courses,user=user,b=b)

@web_routes.post('/action/select_student/add/{b}')
async def action_select_add(request):
    params = await request.post()
    stu_sn =request.match_info.get("b")
    cou_sn = params.get("cou_sn")
 
    if stu_sn is None or cou_sn is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn must be required")
    try:
        stu_sn = int(stu_sn)
        cou_sn = int(cou_sn)
        grade = -1
    except ValueError:
        return web.HTTPBadRequest(text="invalid value")

    try:
        with db_block() as db:
            db.execute("""
            INSERT INTO course_grade (stu_sn, cou_sn, grade) 
            VALUES ( %(stu_sn)s, %(cou_sn)s, %(grade)s)
            """, dict(stu_sn=stu_sn, cou_sn=cou_sn, grade=grade))
    except psycopg2.errors.UniqueViolation:
        return web.HTTPFound(location="/student00")
    except psycopg2.errors.ForeignKeyViolation as ex:
        return web.HTTPBadRequest(text=f"无此学生或课程: {ex}")

@web_routes.post('/action/stu/delete/{stu_sn}/{cou_sn}')
def delete_grade_action(request):
    stu_sn = request.match_info.get("stu_sn")
    cou_sn = request.match_info.get("cou_sn")
    if stu_sn is None or cou_sn is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn, must be required")

    with db_block() as db:
        db.execute("""
        DELETE FROM course_grade
            WHERE stu_sn = %(stu_sn)s AND cou_sn = %(cou_sn)s
        """, dict(stu_sn=stu_sn, cou_sn=cou_sn))

    return web.HTTPFound(location="/student00")