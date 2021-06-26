DELETE FROM course_grade;
DELETE FROM course;
DELETE FROM student;

INSERT INTO student (sn, no, name, gender,enrolled)  VALUES
    (101, 'S001',  '张三','男','2021/10/1'),
    (102, 'S002',  '李四','女','2021/9/1'), 
    (103, 'S003',  '王五','男','2021/8/1'),
    (104, 'S004',  '马六','男','2021/7/1');

INSERT INTO course (sn, no, name, time)  VALUES 
    (101, 'C01',  '高数'  ,'14'), 
    (102, 'C02',  '外语'  ,'24'),
    (103, 'C03',  '线代'  ,'24');


INSERT INTO course_grade (stu_sn, cou_sn, grade)  VALUES 
    (101, 101,  91), 
    (102, 101,  89),
    (103, 101,  90),
    (101, 102,  89);


    