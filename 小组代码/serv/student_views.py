from aiohttp import web
from aiohttp.web_request import Request
from .config import db_block, web_routes, render_html
import psycopg2.errors
from urllib.parse import urlencode

from .config import db_block, web_routes




@web_routes.get("/student")
async def view_list_grades(request):
    with db_block() as db:
        db.execute("""
        SELECT  sn as stu_sn, no as stu_no, name as stu_name , gender as stu_gender , enrolled as stu_enrolled FROM student ORDER BY name
        """)
        students = list(db)
       
        db.execute("""
        SELECT  sn AS cou_sn, name as cou_name FROM course ORDER BY name
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

    return render_html(request, 'student_list.html',
                       students=students,
                       courses=courses,
                       items=items)


@web_routes.post('/student/add')
async def action_grade_add(request):
    params = await request.post()
    stu_sn = params.get("stu_sn")
    stu_no = params.get("stu_no")
    stu_name = params.get("stu_name")
    stu_gender = params.get("stu_gender")
    stu_enrolled = params.get("stu_enrolled")
   
    if stu_sn is None or stu_no is None or stu_name is None:
        return web.HTTPBadRequest(text="stu_sn, stu_no, stu_name must be required   数据为空")

    try:
        stu_sn = int(stu_sn)
        stu_no = str(stu_no)
        stu_gender = str(stu_gender)
        stu_enrolled = str(stu_enrolled)
        stu_name = str(stu_name)
    except ValueError:
        return web.HTTPBadRequest(text="invalid value   错误的信息")
    try:
        with db_block() as db:
            db.execute("""
            INSERT INTO student (sn, no, name,gender)  
            VALUES ( %(stu_sn)s, %(stu_no)s, %(stu_name)s,%(stu_gender)s)
            """, dict(stu_sn = stu_sn,stu_no = stu_no,stu_name = stu_name,stu_gender=stu_gender,stu_enrolled=stu_enrolled))
    except psycopg2.errors.UniqueViolation:
        query = urlencode({
            "message": "已经添加该学生",
            "return": "/student"
        })
        return web.HTTPFound(location=f"/error?{query}")
    except psycopg2.errors.ForeignKeyViolation as ex:
        return web.HTTPBadRequest(text=f"无此学生或课程: {ex}")
    return web.HTTPFound(location="/student")


@web_routes.get('/student/edit/{stu_sn}/{stu_no}/{stu_name}/{stu_gender}')
def view_student_editor(request):
    stu_sn = request.match_info.get("stu_sn")
    stu_no = request.match_info.get("stu_no")
    stu_name = request.match_info.get("stu_name")
    stu_gender = request.match_info.get("stu_gender")
    if stu_sn is None or stu_no is None or stu_name is None:
        return web.HTTPBadRequest(text="stu_sn, must be required")
    with db_block() as db:
        db.execute("""
        SELECT student FROM student
            WHERE sn = %(stu_sn)s ;
        """, dict(stu_sn=stu_sn))

        record = db.fetch_first()

    if record is None:
        return web.HTTPNotFound(text=f"no such student: stu_sn={stu_sn}")

    return render_html(request, "student_edit.html",
                       stu_sn=stu_sn,
                       stu_no=stu_no,
                       stu_name=stu_name,stu_gender=stu_gender)

@web_routes.post('/views/student/edit/{stu_sn}/{stu_no}/{stu_name}/{stu_gender}')
async def edit_grade_action(request):

    params = await request.post()
    stu_sn = params.get("stu_sn")
    stu_no = params.get("stu_no")
    stu_name = params.get("stu_name")
    stu_gender = params.get("stu_gender")
    if stu_sn is None or stu_no is None or stu_name is None:
        return web.HTTPBadRequest(text="stu_sn, stu_no,  stu_name must be required")
    try:
        stu_sn = int(stu_sn)
        stu_no = str(stu_no)
        stu_name = str(stu_name)
    except ValueError:
        return web.HTTPBadRequest(text="invalid value")

    with db_block() as db:
        db.execute("""
        UPDATE student SET name=%(stu_name)s , gender=%(stu_gender)s , no=%(stu_no)s
        WHERE no = %(stu_no)s
        """, dict(stu_sn=stu_sn, stu_no=stu_no, stu_name=stu_name,stu_gender=stu_gender))
    return web.HTTPFound(location="/student")

@web_routes.get("/student/delete/{stu_sn}/{stu_no}/{stu_name}")
def student_deletion_dialog(request):
    stu_sn = request.match_info.get("stu_sn")
    stu_no = request.match_info.get("stu_no")
    stu_name = request.match_info.get("stu_name")
    if stu_sn is None or stu_no is None or stu_name is None:
        return web.HTTPBadRequest(text="stu_sn, stu_no, stu_name must be required")

    with db_block() as db:
        db.execute("""
        SELECT student FROM student
            WHERE sn = %(stu_sn)s;
        """, dict(stu_sn=stu_sn))
        record = db.fetch_first()

    if record is None:
        return web.HTTPNotFound(text=f"no such student: stu_sn={stu_sn}")

    return render_html(request, 'student_dialog_deletion.html',
                        record=record,
                        stu_sn=stu_sn,
                       stu_no=stu_no,
                       stu_name=stu_name)



@web_routes.post('/views/student/delete/{stu_sn}/{stu_no}/{stu_name}')
def delete_grade_action(request):
    stu_sn = request.match_info.get("stu_sn")
    if stu_sn is None:
        return web.HTTPBadRequest(text="stu_sn, stu_no, stu_name must be required")
    stu_sn=int(stu_sn)
    try:    
        with db_block() as db:
            db.execute("""
            DELETE FROM student
                WHERE sn = %(stu_sn)s
            """, dict(stu_sn=stu_sn))
    except psycopg2.errors.UniqueViolation:
        query = urlencode({
            "message": "已经添加该学生",
            "return": "/student"
        })
    except psycopg2.errors.ForeignKeyViolation as ex:
        return web.HTTPBadRequest(text=f"此学生已有课程或成绩: {ex}")

    return web.HTTPFound(location="/student")

@web_routes.get("/students")
async def view_list_grades(request):
    user = request.match_info.get("users")
    params = await request.post()
    t = params.get("t")
    if t is None:
        t=-1
    else:
        t=int(t)
    user=user
    with db_block() as db:
        db.execute("""
            SELECT *
            FROM student
            WHERE no=%(user)s;
            """,dict(user=user))
        students = list(db)
        for x in students:
            a=x.sn
       
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
        WHERE stu_sn=%(b)s and g.grade=%(t)s
        """,dict(b=a,t=t))
        items = list(db)
        a=box(items)
        db.execute("""
        SELECT g.stu_sn, g.cou_sn, 
            s.name as stu_name, 
            c.name as cou_name,
            c.no as cou_no,
            g.grade 
        FROM course_grade as g
            INNER JOIN student as s ON g.stu_sn = s.sn
            INNER JOIN course as c  ON g.cou_sn = c.sn
    
        WHERE grade >0;
        """)
        # c=[]
        grades = list(db)

    return render_html(request, 'student.html',students=students,items=items,a=a,grades=grades,user=user)

def box(p):
    
    b=[[],[],[],[],[]]
    for i in range (5):
        a=[0,[],[],[],[],[],[],[]]
        for j in range (7):
            for e in p:
                x=int(e.cou_no[1])-1
            
                y=int(e.cou_no[3])-1
                if i==y and j==x:
                    a[j+1]=e
        b[i]=a
        b[i][0]=i+1
    return b
@web_routes.post("/student01/{user}")
async def view_list_grades(request):
    user = request.match_info.get("user")
    params = await request.post()
    t = params.get("t")
    if t is None:
        t=-1
    else:
        t=int(t)
   
    with db_block() as db:
        db.execute("""
            SELECT *
            FROM student
            WHERE no=%(user)s;
            """,dict(user=user))
        students = list(db)
        for x in students:
            a=x.sn
       
        items=ccc(a,t)
        a=box(items)
        db.execute("""
        SELECT g.stu_sn, g.cou_sn, 
            s.name as stu_name, 
            c.name as cou_name,
            c.no as cou_no,
            g.grade 
        FROM course_grade as g
            INNER JOIN student as s ON g.stu_sn = s.sn
            INNER JOIN course as c  ON g.cou_sn = c.sn
    
        WHERE grade >0;
        """)
        # c=[]
        grades = list(db)
    
    return render_html(request, 'student.html',students=students,items=items,a=a,grades=grades,user=user)

def ccc(a,t):
    with db_block() as db:
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
        WHERE stu_sn=%(b)s and g.grade=%(t)s
        """,dict(b=a,t=t))
        items = list(db)
        return items