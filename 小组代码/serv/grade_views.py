from aiohttp import web
from .config import db_block, web_routes, render_html


@web_routes.get("/grade")
async def view_list_grades(request):
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
    
        WHERE grade >= 0;
        """)
        # c=[]
        items = list(db)
        # for i in items:
        #     if i.grade==-1:
        #         i=c
    return render_html(request, 'grade_list.html',
                       students=students,
                       courses=courses,
                       items=items)


@web_routes.get('/grade/edit/{stu_sn}/{cou_sn}')
def view_grade_editor(request):
    stu_sn = request.match_info.get("stu_sn")
    cou_sn = request.match_info.get("cou_sn")
    if stu_sn is None or cou_sn is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn, must be required")

    with db_block() as db:
        db.execute("""
        SELECT grade FROM course_grade
            WHERE stu_sn = %(stu_sn)s AND cou_sn = %(cou_sn)s;
        """, dict(stu_sn=stu_sn, cou_sn=cou_sn))

        record = db.fetch_first()

    if record is None:
        return web.HTTPNotFound(text=f"no such grade: stu_sn={stu_sn}, cou_sn={cou_sn}")

    return render_html(request, "grade_edit.html",
                       stu_sn=stu_sn,
                       cou_sn=cou_sn,
                       grade=record.grade)


@web_routes.get("/grade/delete/{stu_sn}/{cou_sn}")
def grade_deletion_dialog(request):
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

    return render_html(request, 'grade_dialog_deletion.html', record=record)
