DROP TABLE IF EXISTS student;
CREATE TABLE IF NOT EXISTS student  (
    sn       INTEGER,     --序号
    no       VARCHAR(10), --学号
    name     TEXT,        --姓名
    gender   TEXT,        --性别(F/M/O)
    enrolled TEXT,        --入学时间
    PRIMARY KEY(sn)
);


-- 给sn创建一个自增序号
CREATE SEQUENCE seq_student_sn 
    START 10000 INCREMENT 1 OWNED BY student.sn;
ALTER TABLE student ALTER sn 
    SET DEFAULT nextval('seq_student_sn');
-- 学号唯一
CREATE UNIQUE INDEX idx_student_no ON student(no);

-- === 课程表
DROP TABLE IF EXISTS course;
CREATE TABLE IF NOT EXISTS course  (
    sn       INTEGER,     --序号
    no       VARCHAR(10), --课程号
    name     TEXT,        --课程名称
    PRIMARY KEY(sn)
 
);
CREATE SEQUENCE seq_course_sn 
    START 10000 INCREMENT 1 OWNED BY course.sn;
ALTER TABLE course ALTER sn 
    SET DEFAULT nextval('seq_course_sn');
CREATE UNIQUE INDEX idx_course_no ON course(no);



DROP TABLE IF EXISTS course_grade;
CREATE TABLE IF NOT EXISTS course_grade  (
    stu_sn INTEGER,     -- 学生序号
    cou_sn INTEGER,     -- 课程序号
    grade  NUMERIC(5,2), -- 最终成绩
    PRIMARY KEY(stu_sn, cou_sn)
);

ALTER TABLE course_grade 
    ADD CONSTRAINT stu_sn_fk FOREIGN KEY (stu_sn) REFERENCES student(sn);
ALTER TABLE course_grade 
    ADD CONSTRAINT cou_sn_fk FOREIGN KEY (cou_sn) REFERENCES course(sn);


DROP TABLE IF EXISTS teacher;
CREATE TABLE IF NOT EXISTS teacher  (
    sn       INTEGER,     --编号
    no       VARCHAR(10), --教师号
    name     TEXT,        --姓名
    gender   TEXT,        --性别(F/M/O)
    college  TEXT,        --学院
    PRIMARY KEY(sn)
);
-- 给sn创建一个自增序号
CREATE SEQUENCE seq_teacher_sn 
    START 10000 INCREMENT 1 OWNED BY teacher.sn;
ALTER TABLE teacher ALTER sn 
    SET DEFAULT nextval('seq_teacher_sn');
-- 学号唯一
CREATE UNIQUE INDEX idx_teacher_no ON teacher(no);