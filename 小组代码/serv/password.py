from aiohttp import web
from .config import db_block, web_routes, render_html
import psycopg2.errors
from urllib.parse import urlencode

@web_routes.post("/login")
async def handle_login(request):
    parmas = await request.post()  # 获取POST请求的表单字段数据
    global username
    username = parmas.get("username")
    password = parmas.get("password")
    if username is None or password is None:
        return web.HTTPFound('/login')  
    with db_block() as db:
        db.execute("""
        SELECT  sn as stu_sn, no as stu_no, name as stu_name , gender as stu_gender , enrolled as stu_enrolled 
        FROM student 
        WHERE no = %(stu_no)s
        """,dict(stu_no=username))
        students = list(db)     

    for student in students:
        user=str(student.stu_no)
        pas=student.stu_no
        users=int(student.stu_no)
    
    passwords={user:pas}
    
    if user[8]+user[9] != str(password):  # 比较密码
        return web.HTTPFound('/login')  # 比对失败重新登录

    # set_secure_cookie(resp, "session_id", username)
    else:
        
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

@web_routes.post("/login1")
async def handle_login(request):
    parmas = await request.post()  # 获取POST请求的表单字段数据
    global username
    username = parmas.get("username")
    password = parmas.get("password")
    with db_block() as db:
        db.execute("""
        SELECT  sn as stu_sn, no as stu_no, name as stu_name , gender as stu_gender , enrolled as stu_enrolled 
        FROM student 
        WHERE no = %(stu_no)s
        """,dict(stu_no=username))
        students = list(db)     

    for student in students:
        user=str(student.stu_no)
        pas=student.stu_no
        users=int(student.stu_no)
    
    passwords={user:pas}
    
    if user[8]+user[9] != str(password):  # 比较密码
        return web.HTTPFound('/login')  # 比对失败重新登录

    # set_secure_cookie(resp, "session_id", username)
    else:
        
        return web.HTTPFound('/teacher00')


        
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