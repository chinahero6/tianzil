from os import path
from threading import stack_size
from aiohttp import web
from aiohttp.web_exceptions import HTTPTooManyRequests
from aiohttp.web_routedef import static
import jinja2
from pathlib import Path
from jinja2.utils import url_quote
from serv.config import web_routes, home_path

# import serv.first
import serv.error_views
import serv.main_views
import serv.grade_views
import serv.student_views
import serv.grade_actions
import serv.select_views
import serv.courses_views
import serv.password
from dbconn import db_block


from serv.config import web_routes, home_path

from cryptography.fernet import InvalidToken
from cryptography.fernet import Fernet
secret_key = Fernet.generate_key()
fernet = Fernet(secret_key)




home_path1 = str(Path(__file__).parent.parent)
print(home_path1)
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(home_path1))

async def home_page(request):
    template = jinja_env.get_template('home.html')
    return web.Response(text=template.render(),
                        content_type="text/html")

async def login_form_page(request):
    return web.Response(text="""
    <html lang='en'>
    <head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>天津工业大学</title>
    <link rel="stylesheet" type="text/css" href="login.css" >

    </head>

    <body>
    <div class="switch"><h2>没有/已有账号？</h2></div>
    <input type="checkbox" style="display: none;" id="change">
    <label for="change">切 换</label>

    
    
    <div class='turn'>
        <div class='over'>
            <form action="/login" method="post" class='login'>
            
            <input type="text" name="username" placeholder="用户名">
            <input type="password" name="password" placeholder="密码">
            <input type="submit" value="登录" class='btn'>
            </form>
            
            <form action="/" method="get" class='sign'>
        
            <input type="submit" value="返回身份选择界面" class='btns'>
        </form>
                  

        </div>
    </div>
 <canvas id="sakura"></canvas>

  <!-- sakura shader -->
  <script id="sakura_point_vsh" type="x-shader/x_vertex">
  uniform mat4 uProjection;
  uniform mat4 uModelview;
  uniform vec3 uResolution;
  uniform vec3 uOffset;
  uniform vec3 uDOF;  //x:focus distance, y:focus radius, z:max radius
  uniform vec3 uFade; //x:start distance, y:half distance, z:near fade start
  
  attribute vec3 aPosition;
  attribute vec3 aEuler;
  attribute vec2 aMisc; //x:size, y:fade
  
  varying vec3 pposition;
  varying float psize;
  varying float palpha;
  varying float pdist;
  
  //varying mat3 rotMat;
  varying vec3 normX;
  varying vec3 normY;
  varying vec3 normZ;
  varying vec3 normal;
  
  varying float diffuse;
  varying float specular;
  varying float rstop;
  varying float distancefade;
  
  void main(void) {
      // Projection is based on vertical angle
      vec4 pos = uModelview * vec4(aPosition + uOffset, 1.0);
      gl_Position = uProjection * pos;
      gl_PointSize = aMisc.x * uProjection[1][1] / -pos.z * uResolution.y * 0.5;
      
      pposition = pos.xyz;
      psize = aMisc.x;
      pdist = length(pos.xyz);
      palpha = smoothstep(0.0, 1.0, (pdist - 0.1) / uFade.z);
      
      vec3 elrsn = sin(aEuler);
      vec3 elrcs = cos(aEuler);
      mat3 rotx = mat3(
          1.0, 0.0, 0.0,
          0.0, elrcs.x, elrsn.x,
          0.0, -elrsn.x, elrcs.x
      );
      mat3 roty = mat3(
          elrcs.y, 0.0, -elrsn.y,
          0.0, 1.0, 0.0,
          elrsn.y, 0.0, elrcs.y
      );
      mat3 rotz = mat3(
          elrcs.z, elrsn.z, 0.0, 
          -elrsn.z, elrcs.z, 0.0,
          0.0, 0.0, 1.0
      );
      mat3 rotmat = rotx * roty * rotz;
      normal = rotmat[2];
      
      mat3 trrotm = mat3(
          rotmat[0][0], rotmat[1][0], rotmat[2][0],
          rotmat[0][1], rotmat[1][1], rotmat[2][1],
          rotmat[0][2], rotmat[1][2], rotmat[2][2]
      );
      normX = trrotm[0];
      normY = trrotm[1];
      normZ = trrotm[2];
      
      const vec3 lit = vec3(0.6917144638660746, 0.6917144638660746, -0.20751433915982237);
      
      float tmpdfs = dot(lit, normal);
      if(tmpdfs < 0.0) {
          normal = -normal;
          tmpdfs = dot(lit, normal);
      }
      diffuse = 0.4 + tmpdfs;
      
      vec3 eyev = normalize(-pos.xyz);
      if(dot(eyev, normal) > 0.0) {
          vec3 hv = normalize(eyev + lit);
          specular = pow(max(dot(hv, normal), 0.0), 20.0);
      }
      else {
          specular = 0.0;
      }
      
      rstop = clamp((abs(pdist - uDOF.x) - uDOF.y) / uDOF.z, 0.0, 1.0);
      rstop = pow(rstop, 0.5);
      //-0.69315 = ln(0.5)
      distancefade = min(1.0, exp((uFade.x - pdist) * 0.69315 / uFade.y));
  }
  </script>
  <script id="sakura_point_fsh" type="x-shader/x_fragment">
  #ifdef GL_ES
  //precision mediump float;
  precision highp float;
  #endif
  
  uniform vec3 uDOF;  //x:focus distance, y:focus radius, z:max radius
  uniform vec3 uFade; //x:start distance, y:half distance, z:near fade start
  
  const vec3 fadeCol = vec3(0.08, 0.03, 0.06);
  
  varying vec3 pposition;
  varying float psize;
  varying float palpha;
  varying float pdist;
  
  //varying mat3 rotMat;
  varying vec3 normX;
  varying vec3 normY;
  varying vec3 normZ;
  varying vec3 normal;
  
  varying float diffuse;
  varying float specular;
  varying float rstop;
  varying float distancefade;
  
  float ellipse(vec2 p, vec2 o, vec2 r) {
      vec2 lp = (p - o) / r;
      return length(lp) - 1.0;
  }
  
  void main(void) {
      vec3 p = vec3(gl_PointCoord - vec2(0.5, 0.5), 0.0) * 2.0;
      vec3 d = vec3(0.0, 0.0, -1.0);
      float nd = normZ.z; //dot(-normZ, d);
      if(abs(nd) < 0.0001) discard;
      
      float np = dot(normZ, p);
      vec3 tp = p + d * np / nd;
      vec2 coord = vec2(dot(normX, tp), dot(normY, tp));
      
      //angle = 15 degree
      const float flwrsn = 0.258819045102521;
      const float flwrcs = 0.965925826289068;
      mat2 flwrm = mat2(flwrcs, -flwrsn, flwrsn, flwrcs);
      vec2 flwrp = vec2(abs(coord.x), coord.y) * flwrm;
      
      float r;
      if(flwrp.x < 0.0) {
          r = ellipse(flwrp, vec2(0.065, 0.024) * 0.5, vec2(0.36, 0.96) * 0.5);
      }
      else {
          r = ellipse(flwrp, vec2(0.065, 0.024) * 0.5, vec2(0.58, 0.96) * 0.5);
      }
      
      if(r > rstop) discard;
      
      vec3 col = mix(vec3(1.0, 0.8, 0.75), vec3(1.0, 0.9, 0.87), r);
      float grady = mix(0.0, 1.0, pow(coord.y * 0.5 + 0.5, 0.35));
      col *= vec3(1.0, grady, grady);
      col *= mix(0.8, 1.0, pow(abs(coord.x), 0.3));
      col = col * diffuse + specular;
      
      col = mix(fadeCol, col, distancefade);
      
      float alpha = (rstop > 0.001)? (0.5 - r / (rstop * 2.0)) : 1.0;
      alpha = smoothstep(0.0, 1.0, alpha) * palpha;
      
      gl_FragColor = vec4(col * 0.5, alpha);
  }
  </script>
  <!-- effects -->
  <script id="fx_common_vsh" type="x-shader/x_vertex">
  uniform vec3 uResolution;
  attribute vec2 aPosition;
  
  varying vec2 texCoord;
  varying vec2 screenCoord;
  
  void main(void) {
      gl_Position = vec4(aPosition, 0.0, 1.0);
      texCoord = aPosition.xy * 0.5 + vec2(0.5, 0.5);
      screenCoord = aPosition.xy * vec2(uResolution.z, 1.0);
  }
  </script>
  <script id="bg_fsh" type="x-shader/x_fragment">
  #ifdef GL_ES
  //precision mediump float;
  precision highp float;
  #endif
  
  uniform vec2 uTimes;
  
  varying vec2 texCoord;
  varying vec2 screenCoord;
  
  void main(void) {
      vec3 col;
      float c;
      vec2 tmpv = texCoord * vec2(0.8, 1.0) - vec2(0.95, 1.0);
      c = exp(-pow(length(tmpv) * 1.8, 2.0));
      col = mix(vec3(0.02, 0.0, 0.03), vec3(0.96, 0.98, 1.0) * 1.5, c);
      gl_FragColor = vec4(col * 0.5, 1.0);
  }
  </script>
  <script id="fx_brightbuf_fsh" type="x-shader/x_fragment">
  #ifdef GL_ES
  //precision mediump float;
  precision highp float;
  #endif
  uniform sampler2D uSrc;
  uniform vec2 uDelta;
  
  varying vec2 texCoord;
  varying vec2 screenCoord;
  
  void main(void) {
      vec4 col = texture2D(uSrc, texCoord);
      gl_FragColor = vec4(col.rgb * 2.0 - vec3(0.5), 1.0);
  }
  </script>
  <script id="fx_dirblur_r4_fsh" type="x-shader/x_fragment">
  #ifdef GL_ES
  //precision mediump float;
  precision highp float;
  #endif
  uniform sampler2D uSrc;
  uniform vec2 uDelta;
  uniform vec4 uBlurDir; //dir(x, y), stride(z, w)
  
  varying vec2 texCoord;
  varying vec2 screenCoord;
  
  void main(void) {
      vec4 col = texture2D(uSrc, texCoord);
      col = col + texture2D(uSrc, texCoord + uBlurDir.xy * uDelta);
      col = col + texture2D(uSrc, texCoord - uBlurDir.xy * uDelta);
      col = col + texture2D(uSrc, texCoord + (uBlurDir.xy + uBlurDir.zw) * uDelta);
      col = col + texture2D(uSrc, texCoord - (uBlurDir.xy + uBlurDir.zw) * uDelta);
      gl_FragColor = col / 5.0;
  }
  </script>
  <!-- effect fragment shader template -->
  <script id="fx_common_fsh" type="x-shader/x_fragment">
  #ifdef GL_ES
  //precision mediump float;
  precision highp float;
  #endif
  uniform sampler2D uSrc;
  uniform vec2 uDelta;
  
  varying vec2 texCoord;
  varying vec2 screenCoord;
  
  void main(void) {
      gl_FragColor = texture2D(uSrc, texCoord);
  }
  </script>
  <!-- post processing -->
  <script id="pp_final_vsh" type="x-shader/x_vertex">
  uniform vec3 uResolution;
  attribute vec2 aPosition;
  varying vec2 texCoord;
  varying vec2 screenCoord;
  void main(void) {
      gl_Position = vec4(aPosition, 0.0, 1.0);
      texCoord = aPosition.xy * 0.5 + vec2(0.5, 0.5);
      screenCoord = aPosition.xy * vec2(uResolution.z, 1.0);
  }
  </script>
  <script id="pp_final_fsh" type="x-shader/x_fragment">
  #ifdef GL_ES
  //precision mediump float;
  precision highp float;
  #endif
  uniform sampler2D uSrc;
  uniform sampler2D uBloom;
  uniform vec2 uDelta;
  varying vec2 texCoord;
  varying vec2 screenCoord;
  void main(void) {
      vec4 srccol = texture2D(uSrc, texCoord) * 2.0;
      vec4 bloomcol = texture2D(uBloom, texCoord);
      vec4 col;
      col = srccol + bloomcol * (vec4(1.0) + srccol);
      col *= smoothstep(1.0, 0.0, pow(length((texCoord - vec2(0.5)) * 2.0), 1.2) * 0.5);
      col = pow(col, vec4(0.45454545454545)); //(1.0 / 2.2)
      
      gl_FragColor = vec4(col.rgb, 1.0);
      gl_FragColor.a = 1.0;
  }
  </script>
  <!-- partial -->
  <script  src="sakura.js"></script>


</body>
</html>
    """, content_type="text/html")


# def register_db_block(dsn):
#     db_pool = ThreadedConnectionPool(minconn=2, maxconn=10, dsn=dsn)
# def db_block():
#         conn = db_pool.getconn()
#         try:
#             with conn.cursor() as cur:
#                 yield RecordCursor(cur)
#                 conn.commit()
#         except:
#             conn.rollback()
#             raise
#         finally:
#             db_pool.putconn(conn)
#         return db_block

passwords={'tom':'123'}
async def handle_login(request):
    parmas = await request.post()  # 获取POST请求的表单字段数据
    global username
    username = parmas.get("username")
    password = parmas.get("password")

    if passwords.get(username) != password:  # 比较密码
        return web.HTTPFound('/login')  # 比对失败重新登录
    resp = web.HTTPFound('/grade')
    # set_secure_cookie(resp, "session_id", username)
    return resp


passwords2={'wang':'123'}
async def login_form_page2(request):
    template = jinja_env.get_template('login2.html')
    return web.Response(text=template.render(),
                        content_type="text/html")


async def handle_login2(request):
    parmas = await request.post()  # 获取POST请求的表单字段数据
    global username2
    username2 = parmas.get("username")
    password = parmas.get("password")
    # print("username2:",username2,type(username2))
    # print("password:",password,type(password))
    # print("passwords2.get(username2):",passwords2.get(username2),type(passwords2.get(username2)))
    if passwords2.get(username2) != password:  # 比较密码
        return web.HTTPFound('/login2')  # 比对失败重新登录
    resp = web.HTTPFound('/base')
    # set_secure_cookie(resp, "session_id", username2)
    return resp


async def handle_login3(request):
    parmas = await request.post()  # 获取POST请求的表单字段数据
    global username2
    username2 = parmas.get("username")
    password = parmas.get("password")
    print("username2:",username2,type(username2))
    print("password:",password,type(password))
    print("passwords2.get(username2):",passwords2.get(username2),type(passwords2.get(username2)))
    if passwords2.get(username2) != password:  # 比较密码
        return web.HTTPFound('/login3')  # 比对失败重新登录
    resp = web.HTTPFound('/teacher')
    set_secure_cookie(resp, "session_id", username2)
    return resp

def set_secure_cookie(response, name, value, **kwargs):
    value = fernet.encrypt(value.encode('utf-8')).decode('utf-8')
    response.set_cookie(name, value, **kwargs)

home_path = Path(__file__).parent
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(home_path)))

async def login_form_page3(request):
    template = jinja_env.get_template('login3.html')
    return web.Response(text=template.render(),
                        content_type="text/html")
with db_block() as db:
    db.execute('''
    select sn,Staff_no from course1;
    ''')
    items = tuple([tuple(row) for row in db])
passwords2=dict((y, x) for x, y in items)
async def teacher(request):
    with db_block() as db:
        db.execute('''
        select name,data,time,place
        from course1
        where Staff_no=%(Staff_no)s ;
        ''',dict(Staff_no=username2))
        items4 = [row for row in db]
    template = jinja_env.get_template('teacher.html')
    return web.Response(text=template.render(items4=items4),
                        content_type="text/html")
#####教师
async def check_schedule(request):
    datas =await request.post() 
    data = datas.get("semester")
    with db_block() as db:
        db.execute("""
        select name,data,place
        from course1
        where Staff_no=%(Staff_no)s 
        and data=%(data)s;
        """,dict(Staff_no=username2,data=data))
        items5 = [row for row in db]
        template = jinja_env.get_template('teacher2.html')
    return web.Response(text=template.render(items5=items5),
                           content_type="text/html")

###教师
async def check_kecheng(request):
    datas =await request.post() 
    data = datas.get("semester")
    with db_block() as db:
        db.execute("""
        select student1.name,stu_sn,grade
        from course1,course_grade1,student1
        where Staff_no=%(Staff_no)s 
        and stu_sn=student1.sn
        and course1.name=%(data)s;
        """,dict(Staff_no=username2,data=data))
        items50 = [row for row in db]
        template = jinja_env.get_template('teacher3.html')
    return web.Response(text=template.render(items50=items50),
                           content_type="text/html")
#######教师
async def edit_grade_action(request):
    stu_sn = request.match_info.get("stu_sn")
    cou_sn = request.match_info.get("cou_sn")
    if stu_sn is None or cou_sn is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn, must be required")

    params = await request.post()
    grade = params.get("grade")

    try:
        stu_sn = int(stu_sn)
        cou_sn = int(cou_sn)
        grade = float(grade)
    except ValueError:
        return web.HTTPBadRequest(text="invalid value")

    with db_block() as db:
        db.execute("""
        UPDATE course_grade1 SET grade=%(grade)s
        WHERE stu_sn = %(stu_sn)s 
        AND cou_sn = %(cou_sn)s
        """, dict(stu_sn=stu_sn, cou_sn=cou_sn, grade=grade))

    return web.HTTPFound(location="/")


app = web.Application()
app.add_routes(web_routes)
app.add_routes([#web.static("/h", home_path / "static"),
 web.get('/teacher',teacher),
                web.get('/login3',login_form_page3),
                web.post('/login3',handle_login3),
                
                web.post('/teacher/schedule', check_schedule),
                web.post('/teacher/kecheng', check_kecheng),
                web.post('/login2',handle_login2),
                web.get('/login',login_form_page),
     
                web.get('/login2',login_form_page2),
               
                web.get('/',home_page),
                web.static('/',home_path/'static'),

])

if __name__ == "__main__":
    web.run_app(app, port=8080)
