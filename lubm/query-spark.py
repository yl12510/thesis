import sys

import pyspark
from pyspark.sql import SQLContext
from pyspark.sql.types import Row, StructField, StructType, StringType, IntegerType

import datetime

persistLevel = pyspark.StorageLevel.OFF_HEAP

def lubm_q1(sc, aboxPath, partitions):
    """
    --Query 1
    SELECT COUNT (id)
    FROM GraduateStudent
    JOIN takesCourse
    ON GraduateStudent.id = takesCourse.domain
    WHERE takesCourse.range = 'http://www.Department0.University0.edu/GraduateCourse0';
    """
    """
    SELECT ?X
    WHERE
    {?X rdf:type ub:GraduateStudent .
    ?X ub:takesCourse
    http://www.Department0.University0.edu/GraduateCourse0}

    """

    # record the start time of excuting this query
    start = datetime.datetime.now()
    
    # read data from the two csv files
    GraduateStudent = sc.textFile(aboxPath + "GraduateStudent" + "/")
    takesCourse = sc.textFile(aboxPath + "takesCourse" + "/")
    
    # condition of range in the WHERE clause
    ran = "<http://www.Department0.University0.edu/GraduateCourse0>" 

    # WHERE takesCourse.range = 'http://www.Department0.University0.edu/GraduateCourse0'
    domTakesCourse = takesCourse.filter(lambda x : ran == x.split(",")[1]).map(lambda x : x.split(",")[0]).persist(persistLevel)
    GraduateStudent.persist(persistLevel)

    ans = domTakesCourse.intersection(GraduateStudent)

    ans.persist(persistLevel)
    numAns = ans.count()

    # record the end of excuting this query
    end = datetime.datetime.now()
    
    print("**** The number of answers to LUBM query 1 is %i ****" % numAns)
    print("**** The time used for LUBM query 1 is %s " % str(end - start))

    return end - start

def lubm_q2(sc, aboxPath, partitions):
    """
    --Query 2
    SELECT COUNT (GraduateStudent.id)
    FROM GraduateStudent,
     University,
     Department,
     memberOf,
     subOrganizationOf,
     undergraduateDegreeFrom
    WHERE GraduateStudent.id = memberOf.domain
    AND memberOf.range = Department.id
    AND Department.id = subOrganizationOf.domain
    AND subOrganizationOf.range = University.id
    AND GraduateStudent.id = undergraduateDegreeFrom.domain
    AND undergraduateDegreeFrom.range = University.id;
    """
    """
    SELECT ?X, ?Y, ?Z
    WHERE
    {?X rdf:type ub:GraduateStudent .
    ?Y rdf:type ub:University .
    ?Z rdf:type ub:Department .
    ?X ub:memberOf ?Z .
    ?Z ub:subOrganizationOf ?Y .
    ?X ub:undergraduateDegreeFrom ?Y}
    """
    # record the start of executing this query
    start = datetime.datetime.now()

    # read data from csv files
    GraduateStudent = sc.textFile(aboxPath + "GraduateStudent" + "/")
    University = sc.textFile(aboxPath + "University" + "/")
    Department = sc.textFile(aboxPath + "Department" + "/")
    memberOf = sc.textFile(aboxPath + "memberOf" + "/").persist(persistLevel)
    subOrganizationOf = sc.textFile(aboxPath + "subOrganizationOf" + "/").persist(persistLevel)
    undergraduateDegreeFrom = sc.textFile(aboxPath + "undergraduateDegreeFrom" + "/").persist(persistLevel)
    
    # generate answer to the query
    ranUnd = undergraduateDegreeFrom.map(lambda x :  (x.split(",")[1], x.split(",")[0])).partitionBy(partitions).persist(persistLevel)
    pairUniv = University.map(lambda x : (x, x)).persist(persistLevel)
    joinUnivUnd = pairUniv.join(ranUnd).map(lambda (univ, (ranUnd, domUnd)) : (domUnd, (univ, ranUnd))).persist(persistLevel)

    domMem = memberOf.map(lambda x :  (x.split(",")[0], x.split(",")[1])).partitionBy(partitions).persist(persistLevel)    
    joinMemUnivUnd = domMem.join(joinUnivUnd).map(lambda (domMem, (ranMem, (univ, ranUnd))) : (domMem, (univ, ranMem, ranUnd))).persist(persistLevel)

    pairGrad = GraduateStudent.map(lambda x : (x, x)).partitionBy(partitions).persist(persistLevel)
    joinGradMem = pairGrad.join(joinMemUnivUnd).map(lambda (grad, (gradId, (univ, ranMem, ranUnd))): (ranMem, (grad, univ, ranUnd))).persist(persistLevel)

    pairDept = Department.map(lambda x : (x, x)).partitionBy(partitions).persist(persistLevel)
    joinDeptMem = pairDept.join(joinGradMem).map(lambda (dept, (ranMem, (grad, univ, ranUnd))) : ((ranMem, ranUnd), (grad, univ, dept))).persist(persistLevel)
    
    biSubOrgOf = subOrganizationOf.map(lambda x : ((x.split(",")[0], x.split(",")[1]), x)).partitionBy(partitions).persist(persistLevel)

    ans = joinDeptMem.join(biSubOrgOf).map(lambda ((domSub, ranSub), ((grad, univ, dept), x)): (grad, univ, dept)).distinct()

    ans.persist(persistLevel)
    numAns = ans.count()

    # record the end of excuting this query
    end = datetime.datetime.now()
    
    print("**** The number of answers to LUBM query 2 is %i ****" % numAns)
    print("**** The time used for LUBM query 2 is %s " % str(end - start))

    return end - start


def lubm_q3(sc, aboxPath, partitions):
    """
    --Query 3
    SELECT COUNT(id)
    FROM Publication
    JOIN publicationAuthor
    ON Publication.id = publicationAuthor.domain
    WHERE publicationAuthor.range = 'http://www.Department0.University0.edu/AssistantProfessor0';
    """
    
    """
    SELECT ?X
    WHERE
    {?X rdf:type ub:Publication .
    ?X ub:publicationAuthor 
    http://www.Department0.University0.edu/AssistantProfessor0}

    """

    # record the start time of excuting this query
    start = datetime.datetime.now()
    
    # read data from the two csv files
    Publication = sc.textFile(aboxPath + "Publication" + "/")
    pubAuthor = sc.textFile(aboxPath + "publicationAuthor" + "/")

    # condition of range in the WHERE clause
    ran = "<http://www.Department0.University0.edu/AssistantProfessor0>" 

    # WHERE publicationAuthor.range = 'http://www.Department0.University0.edu/AssistantProfessor0'
    domPubAuthor = pubAuthor.filter(lambda x : ran == x.split(",")[1]).map(lambda x : x.split(",")[0]).persist(persistLevel)
    Publication.persist(persistLevel)
    
    ans = domPubAuthor.intersection(Publication)
    ans.persist(persistLevel)

    numAns = ans.count()

    # record the end of excuting this query
    end = datetime.datetime.now()
    
    print("**** The number of answers to LUBM query 3 is %i ****" % numAns)
    print("**** The time used for LUBM query 3 is %s " % str(end - start))

    return end - start

def lubm_q4(sc, aboxPath, partitions):
    """
    --Query 4
    SELECT count (Professor.id)
    FROM Professor,
     worksFor,
     name,
     emailAddress,
     telephone
    WHERE worksFor.range = 'http://www.Department0.University0.edu'
    AND   Professor.id = worksFor.domain
    AND   Professor.id = name.domain
    AND   Professor.id = emailAddress.domain
    AND   Professor.id = telephone.domain;
    """

    """
    SELECT ?X, ?Y1, ?Y2, ?Y3
    WHERE
    {?X rdf:type ub:Professor .
    ?X ub:worksFor <http://www.Department0.University0.edu> .
    ?X ub:name ?Y1 .
    ?X ub:emailAddress ?Y2 .
    ?X ub:telephone ?Y3}
    """

    # record the start time of excuting this query
    start = datetime.datetime.now()

    # read data from csv files
    Professor = sc.textFile(aboxPath + "Professor" + "/")
    worksFor = sc.textFile(aboxPath + "worksFor" + "/")
    name = sc.textFile(aboxPath + "name" + "/")
    emailAddress = sc.textFile(aboxPath + "emailAddress" + "/")
    telephone = sc.textFile(aboxPath + "telephone" + "/")

    # range condition in the WHERE clause
    ran = "<http://www.Department0.University0.edu>"
    
    # generate the answer to the query
    domWorksFor = worksFor.filter(lambda x : ran == x.split(",")[1]).map(lambda x : (x.split(",")[0], x.split(",")[0])).persist(persistLevel)
    domName = name.map(lambda x : (x.split(",")[0], x.split(",")[1])).partitionBy(partitions).persist(persistLevel)
    joinNameWork = domName.join(domWorksFor).map(lambda (domName, (ranName, domWork)) : (domName, ranName)).persist(persistLevel)

    domTel = telephone.map(lambda x : (x.split(",")[0], x.split(",")[1])).partitionBy(partitions).persist(persistLevel)
    joinTelName = domTel.join(joinNameWork).persist(persistLevel) # lambda (domTel, (ranTel, ranName))
    
    domEmail = emailAddress.map(lambda x : (x.split(",")[0], x.split(",")[1])).partitionBy(partitions).persist(persistLevel)
    joinEmailTelName = domEmail.join(joinTelName).map(lambda (domEmail, (ranEmail, (ranTel, ranName))) : (domEmail, (ranName, ranEmail, ranTel))).persist(persistLevel)

    pairPro = Professor.map(lambda x : (x, x)).partitionBy(partitions).persist(persistLevel)
    
    ans = pairPro.join(joinEmailTelName).map(lambda (pro, (domEmail, (ranName, ranEmail, ranTel))): (pro, ranName, ranEmail, ranTel)).distinct()
    ans.persist(persistLevel)

    numAns = ans.count()

    # record the end of excuting this query
    end = datetime.datetime.now()
    
    print("**** The number of answers to LUBM query 4 is %i ****" % numAns)
    print("**** The time used for LUBM query 4 is %s " % str(end - start))

    return end - start

    
def lubm_q5(sc, aboxPath, partitions): 
    """
    --Query 5
    SELECT count (Person.id)
    FROM Person, memberOf
    WHERE Person.id = memberOf.domain
    AND memberOf.range = 'http://www.Department0.University0.edu';
    """
    """
    SELECT ?X
    WHERE
    {?X rdf:type ub:Person .
    ?X ub:memberOf <http://www.Department0.University0.edu>}
    """
    
    # record the start time of excuting this query
    start = datetime.datetime.now()
    
    # read data from the two csv files
    Person = sc.textFile(aboxPath + "Person" + "/")
    memberOf = sc.textFile(aboxPath + "memberOf" + "/")

    # condition of range in the WHERE clause
    ran = "<http://www.Department0.University0.edu>" 

    # WHERE memberOf.range = 'http://www.Department0.University0.edu'
    domMemOf = memberOf.filter(lambda x : ran == x.split(",")[1]).map(lambda x : x.split(",")[0]).persist(persistLevel)
    Person.persist(persistLevel)
    
    ans = domMemOf.intersection(Person)
    ans.persist(persistLevel)

    numAns = ans.count()

    # record the end of excuting this query
    end = datetime.datetime.now()
    
    print("**** The number of answers to LUBM query 5 is %i ****" % numAns)
    print("**** The time used for LUBM query 5 is %s " % str(end - start))

    return end - start


def lubm_q6(sc, aboxPath, partitions):
    """
    --Query 6
    SELECT  count (id)
    FROM Student;
    """
    """
    SELECT ?X WHERE {?X rdf:type ub:Student}
    """

    # record the start time of executing query 6
    start = datetime.datetime.now()

    # read data from related csv file
    Student = sc.textFile(aboxPath + "Student" + "/")

    ans = Student
    ans.persist(persistLevel)

    numAns = ans.count()    
    
    # record the end of excuting this query
    end = datetime.datetime.now()
    
    print("**** The number of answers to LUBM query 6 is %i ****" % numAns)
    print("**** The time used for LUBM query 6 is %s " % str(end - start))

    return end - start


def lubm_q7(sc, aboxPath, partitions):
    """
    --Query 7
    SELECT count (Student.id)
    FROM   Student, Course, takesCourse, teacherOf
    WHERE  Student.id = takesCourse.domain
    AND    takesCourse.range = Course.id
    AND    teacherOf.range = Course.id
    AND    teacherOf.domain = 'http://www.Department0.University0.edu/AssociateProfessor0';
    """
    """
    SELECT ?X, ?Y
    WHERE 
    {?X rdf:type ub:Student .
    ?Y rdf:type ub:Course .
    ?X ub:takesCourse ?Y .
    <http://www.Department0.University0.edu/AssociateProfessor0>,   
    ub:teacherOf, ?Y}
    """

    # record the start time of executing this query 
    start = datetime.datetime.now()

    # read data from csv files
    Student = sc.textFile(aboxPath + "Student" + "/")
    Course = sc.textFile(aboxPath + "Course" + "/")
    takesCourse = sc.textFile(aboxPath + "takesCourse" + "/")
    teacherOf = sc.textFile(aboxPath + "teacherOf" + "/")

    # domain condition in the where clause
    dom = "<http://www.Department0.University0.edu/AssociateProfessor0>"

    # generate the answer to the query
    Course = Course.persist(persistLevel)
    ranTeacherOf = teacherOf.filter(lambda x : dom == x.split(",")[0]).map(lambda x : x.split(",")[1]).persist(persistLevel)
    courseTeacher = ranTeacherOf.intersection(Course).map(lambda x : (x,x)).persist(persistLevel)
    ranTakesCourse = takesCourse.map(lambda x: (x.split(",")[1], x.split(",")[0])).partitionBy(partitions).persist(persistLevel)

    joinTakeTea = ranTakesCourse.join(courseTeacher).map(lambda (ranTake, (domTake, cours)): (domTake, cours)).persist(persistLevel)
    pairStud = Student.map(lambda x : (x, x)).partitionBy(partitions).persist(persistLevel)
    
    ans = pairStud.join(joinTakeTea).map(lambda (stud, (studId, cours)): (stud, cours)).distinct()
    ans.persist(persistLevel)

    numAns = ans.count()

    # record the end of excuting this query
    end = datetime.datetime.now()
    
    print("**** The number of answers to LUBM query 7 is %i ****" % numAns)
    print("**** The time used for LUBM query 7 is %s " % str(end - start))

    return end - start

    
def lubm_q8(sc, aboxPath, partitions):
    """
    --Query 8
    SELECT count (Student.id)
    FROM   Student, Department, memberOf, subOrganizationOf, emailAddress
    WHERE  Student.id = memberOf.domain
    AND    Department.id = memberOf.range
    AND    Department.id = subOrganizationOf.domain
    AND    subOrganizationOf.range = 'http://www.University0.edu'
    AND    Student.id = emailAddress.domain;
    """
    """
    SELECT ?X, ?Y, ?Z
    WHERE
    {?X rdf:type ub:Student .
    ?Y rdf:type ub:Department .
    ?X ub:memberOf ?Y .
    ?Y ub:subOrganizationOf <http://www.University0.edu> .
    ?X ub:emailAddress ?Z}
    """
    # record the start time of excuting this query
    start = datetime.datetime.now()

    # read data from csv files
    Student = sc.textFile(aboxPath + "Student" + "/")
    Department = sc.textFile(aboxPath + "Department" + "/")
    memberOf = sc.textFile(aboxPath + "memberOf" + "/")
    subOrganizationOf = sc.textFile(aboxPath + "subOrganizationOf" + "/")
    emailAddress =  sc.textFile(aboxPath + "emailAddress" + "/")

    # range condition in the where clause
    ran = "<http://www.University0.edu>" 
    
    # generate answer to the query 
    domSubOrg = subOrganizationOf.filter(lambda x : ran == x.split(",")[1]).map(lambda x : x.split(",")[0]).persist(persistLevel)
    Department.persist(persistLevel)

    depDomSubOrg = Department.intersection(domSubOrg).map(lambda x: (x,x)).persist(persistLevel)

    ranMemOf = memberOf.map(lambda x : (x.split(",")[1], x.split(",")[0])).partitionBy(partitions).persist(persistLevel)
    joinMemSub = ranMemOf.join(depDomSubOrg).map(lambda (ranMem, (domMem, dept)): (domMem, dept)).persist(persistLevel)
    
    domEmail = emailAddress.map(lambda x : (x.split(",")[0], x.split(",")[1])).partitionBy(partitions).persist(persistLevel)
    joinEmailMem = domEmail.join(joinMemSub).persist(persistLevel) #lambda (domEmail, (ranEmail, dept))

    pairStud = Student.map(lambda x : (x, x)).partitionBy(partitions).persist(persistLevel)

    ans = pairStud.join(joinEmailMem).map(lambda (stud, (studId, (ranEmail, dept))) : (stud, dept, ranEmail)).distinct()
    ans.persist(persistLevel)

    numAns = ans.count()

    # record the end of excuting this query
    end = datetime.datetime.now()
    
    print("**** The number of answers to LUBM query 8 is %i ****" % numAns)
    print("**** The time used for LUBM query 8 is %s " % str(end - start))

    return end - start

    
def lubm_q9(sc, aboxPath, partitions):
    """
    --Query 9
    SELECT count (Student.id)
    FROM   Student,
       Faculty,
       Course,
       advisor,
       teacherOf,
       takesCourse
    WHERE  Student.id = advisor.domain
    AND    advisor.range = Faculty.id
    AND    teacherOf.domain = Faculty.id
    AND    teacherOf.range = Course.id
    AND    takesCourse.domain = Student.id
    AND    takesCourse.range = Course.id;
    """

    """
    SELECT ?X, ?Y, ?Z
    WHERE
    {?X rdf:type ub:Student .
    ?Y rdf:type ub:Faculty .
    ?Z rdf:type ub:Course .
    ?X ub:advisor ?Y .
    ?Y ub:teacherOf ?Z .
    ?X ub:takesCourse ?Z}
    """

    # record the start time of executing this query
    start = datetime.datetime.now()

    # read data from csv files
    Student = sc.textFile(aboxPath + "Student" + "/")
    Faculty = sc.textFile(aboxPath + "Faculty" + "/")
    Course = sc.textFile(aboxPath + "Course" + "/")
    advisor = sc.textFile(aboxPath + "advisor" + "/").persist(persistLevel)
    teacherOf = sc.textFile(aboxPath + "teacherOf" + "/").persist(persistLevel)
    takesCourse = sc.textFile(aboxPath + "takesCourse" + "/").persist(persistLevel)
    
    # generate answer to the query
    ranAdv = advisor.map(lambda x : (x.split(",")[1], x.split(",")[0])).partitionBy(partitions).persist(persistLevel)
    pairFacu = Faculty.map(lambda x : (x, x)).persist(persistLevel)
    joinFacAdv = ranAdv.join(pairFacu).map(lambda (ranAdv, (domAdv, facu)) : (domAdv, (facu, ranAdv))).persist(persistLevel)
    
    domTake = takesCourse.map(lambda x : (x.split(",")[0], x.split(",")[1])).partitionBy(partitions).persist(persistLevel)
    joinTakeAdv = domTake.join(joinFacAdv).map(lambda (domTake, (ranTake, (facu, ranAdv))) : ((ranAdv, ranTake), (facu, domTake))).persist(persistLevel)

    biTea = teacherOf.map(lambda x : ((x.split(",")[0], x.split(",")[1]), x)).partitionBy(partitions).persist(persistLevel)
    joinTeaTakeAdv = biTea.join(joinTakeAdv).map(lambda ((domTea, ranTake), (x, (facu, domTake))) : (ranTake, (domTake, facu))).persist(persistLevel)

    pairCour = Course.map(lambda x : (x, x)).partitionBy(partitions).persist(persistLevel)
    joinCourTake = pairCour.join(joinTeaTakeAdv).map(lambda (ranTake, (cour, (domTake, facu))) : (domTake, (facu, cour))).persist(persistLevel)

    pairStud = Student.map(lambda x : (x, x)).partitionBy(partitions).persist(persistLevel)
    ans = pairStud.join(joinCourTake).map(lambda (stud, (domTake, (facu, cour))) : (stud, facu, cour)).distinct()

    ans.persist(persistLevel)
    numAns = ans.count()

    # record the end of excuting this query
    end = datetime.datetime.now()
    
    print("**** The number of answers to LUBM query 9 is %i ****" % numAns)
    print("**** The time used for LUBM query 9 is %s " % str(end - start))

    return end - start


def lubm_q9_sql(sc, aboxPath, partitions):
    """
    --Query 9
    SELECT count (Student.id)
    FROM   Student,
       Faculty,
       Course,
       advisor,
       teacherOf,
       takesCourse
    WHERE  Student.id = advisor.domain
    AND    advisor.range = Faculty.id
    AND    teacherOf.domain = Faculty.id
    AND    teacherOf.range = Course.id
    AND    takesCourse.domain = Student.id
    AND    takesCourse.range = Course.id;
    """

    # record the start time of executing this query
    start = datetime.datetime.now()

    sqlContext = SQLContext(sc)
    
    # read data from csv files
    Student = sc.textFile(aboxPath + "Student" + "/").map(lambda x : (x,))
    Faculty = sc.textFile(aboxPath + "Faculty" + "/").map(lambda x : (x,))
    Course = sc.textFile(aboxPath + "Course" + "/").map(lambda x : (x,))
    advisor = sc.textFile(aboxPath + "advisor" + "/").map(lambda x : (x.split(",")[0], x.split(",")[1]))
    teacherOf = sc.textFile(aboxPath + "teacherOf" + "/").map(lambda x : (x.split(",")[0], x.split(",")[1]))
    takesCourse = sc.textFile(aboxPath + "takesCourse" + "/").map(lambda x : (x.split(",")[0], x.split(",")[1]))

    
    clsSchema = StructType([StructField("id", StringType(), False)])
    proSchema = StructType([StructField("domain", StringType(), False),
                            StructField("range", StringType(), False)])

    Student_df = sqlContext.createDataFrame(Student, clsSchema)
    Faculty_df = sqlContext.createDataFrame(Faculty, clsSchema)
    Course_df = sqlContext.createDataFrame(Course, clsSchema)

    advisor_df = sqlContext.createDataFrame(advisor, proSchema)
    teacherOf_df = sqlContext.createDataFrame(teacherOf, proSchema)
    takesCourse_df = sqlContext.createDataFrame(takesCourse, proSchema)

    Student_df.registerAsTable("Student")
    Faculty_df.registerAsTable("Faculty")
    Course_df.registerAsTable("Course")
    advisor_df.registerAsTable("advisor")
    teacherOf_df.registerAsTable("teacherOf")
    takesCourse_df.registerAsTable("takesCourse")

    sqlContext.cacheTable("Student")
    sqlContext.cacheTable("Faculty")
    sqlContext.cacheTable("Course")
    sqlContext.cacheTable("advisor")
    sqlContext.cacheTable("teacherOf")
    sqlContext.cacheTable("takesCourse")


    #ans = sqlContext.sql("SELECT count(*) FROM Student")
    
    ans = sqlContext.sql("SELECT count (Student.id) FROM  Student, Faculty, Course, advisor, teacherOf, takesCourse WHERE  Student.id = advisor.domain AND    advisor.range = Faculty.id AND    teacherOf.domain = Faculty.id AND    teacherOf.range = Course.id AND    takesCourse.domain = Student.id AND    takesCourse.range = Course.id")

    for each in ans.collect():
        print each[0]

    # record the end time of executing this query
    end = datetime.datetime.now()
        
    return (end - start) 
    
def lubm_q10(sc, aboxPath, partitions): 
    """
    --Query 10
    SELECT count (Student.id)
    FROM   Student, takesCourse
    WHERE  Student.id = takesCourse.domain
    AND    takesCourse.range = 'http://www.Department0.University0.edu/GraduateCourse0';
    """
    """
    SELECT ?X
    WHERE
    {?X rdf:type ub:Student .
    ?X ub:takesCourse
    <http://www.Department0.University0.edu/GraduateCourse0>}

    """

    # record the start time of excuting this query
    start = datetime.datetime.now()
    
    # read data from the two csv files
    Student = sc.textFile(aboxPath + "Student" + "/")
    takesCourse = sc.textFile(aboxPath + "takesCourse" + "/")

    # condition of range in the WHERE clause
    ran = "<http://www.Department0.University0.edu/GraduateCourse0>" 

    # WHERE takesCourse.range = 'http://www.Department0.University0.edu/GraduateCourse0'
    domTakesCourse = takesCourse.filter(lambda x : ran == x.split(",")[1]).map(lambda x : x.split(",")[0]).persist(persistLevel)
    Student.persist(persistLevel)
    
    ans = domTakesCourse.intersection(Student)
    ans.persist(persistLevel)

    numAns = ans.count()

    # record the end of excuting this query
    end = datetime.datetime.now()
    
    print("**** The number of answers to LUBM query 10 is %i ****" % numAns)
    print("**** The time used for LUBM query 10 is %s " % str(end - start))

    return end - start


def lubm_q11(sc, aboxPath, partitions): 
    """
    --Query 11
    SELECT count (ResearchGroup.id)
    FROM   ResearchGroup, subOrganizationOf
    WHERE  ResearchGroup.id = subOrganizationOf.domain
    AND    subOrganizationOf.range = 'http://www.University0.edu';
    """
    """
    SELECT ?X
    WHERE
    {?X rdf:type ub:ResearchGroup .
    ?X ub:subOrganizationOf <http://www.University0.edu>}
    """

    # record the start time of excuting this query
    start = datetime.datetime.now()
    
    # read data from the two csv files
    ResearchGroup = sc.textFile(aboxPath + "ResearchGroup" + "/")
    subOrganizationOf = sc.textFile(aboxPath + "subOrganizationOf" + "/")
    
    # condition of range in the WHERE clause
    ran = "<http://www.University0.edu>" 

    # WHERE subOrganizationOf.range = 'http://www.University0.edu';
    domSubOrg = subOrganizationOf.filter(lambda x : ran == x.split(",")[1]).map(lambda x : x.split(",")[0]).persist(persistLevel)
    ResearchGroup.persist(persistLevel)

    ans = domSubOrg.intersection(ResearchGroup)
    ans.persist(persistLevel)

    numAns = ans.count()

    # record the end of excuting this query
    end = datetime.datetime.now()
    
    print("**** The number of answers to LUBM query 11 is %i ****" % numAns)
    print("**** The time used for LUBM query 11 is %s " % str(end - start))

    return end - start

def lubm_q12(sc, aboxPath, partitions):
    """
    --Query 12
    SELECT count (Chair.id)
    FROM   Chair, worksFor, subOrganizationOf, Department 
    WHERE  Chair.id = worksFor.domain
    AND    Department.id = subOrganizationOf.domain
    AND    worksFor.range = Department.id 
    AND    subOrganizationOf.range = 'http://www.University0.edu';
    """
    """
    SELECT ?X, ?Y
    WHERE
    {?X rdf:type ub:Chair .
    ?Y rdf:type ub:Department .
    ?X ub:worksFor ?Y .
    ?Y ub:subOrganizationOf <http://www.University0.edu>}

    """
    # record the start time of excuting this query
    start = datetime.datetime.now()

    # read data from related csv files 
    Chair = sc.textFile(aboxPath + "Chair" + "/")
    worksFor = sc.textFile(aboxPath + "worksFor" + "/")
    Department = sc.textFile(aboxPath + "Department" + "/")
    subOrganizationOf = sc.textFile(aboxPath + "subOrganizationOf" + "/")

    # condition of range in the where clause
    ran = "<http://www.University0.edu>"
    
    # subOrganizationOf.range = 'http://www.University0.edu'
    domSubOrg = subOrganizationOf.filter(lambda x : ran == x.split(",")[1]).map(lambda x : x.split(",")[0]).persist(persistLevel)
    Department = Department.persist(persistLevel)
    DepSubOrg = Department.intersection(domSubOrg).map(lambda x : (x, x)).persist(persistLevel)
    
    ranWorksFor = worksFor.map(lambda x : (x.split(",")[1], x.split(",")[0])).partitionBy(partitions).persist(persistLevel)
    joinDeptWorks = ranWorksFor.join(DepSubOrg).map(lambda (ranWorks, (domWorks, dept)): (domWorks, dept)).persist(persistLevel)

    pairChair = Chair.map(lambda x : (x, x)).partitionBy(partitions).persist(persistLevel)
    ans = pairChair.join(joinDeptWorks).map(lambda (chair, (chairId, dept)) : (chair, dept)).distinct()
    ans.persist(persistLevel)

    numAns = ans.count()

    # record the end of excuting this query
    end = datetime.datetime.now()
    
    print("**** The number of answers to LUBM query 12 is %i ****" % numAns)
    print("**** The time used for LUBM query 12 is %s " % str(end - start))

    return end - start

    
def lubm_q13(sc, aboxPath, partitions): 
    """
    --Query 13
    SELECT count (Person.id)
    FROM   Person, hasAlumnus
    WHERE  hasAlumnus.domain = 'http://www.University0.edu'
    AND    hasAlumnus.range = Person.id;
    """
    """
    SELECT ?X
    WHERE
    {?X rdf:type ub:Person .
    <http://www.University0.edu> ub:hasAlumnus ?X}

    """

    # record the start time of excuting this query
    start = datetime.datetime.now()
    
    # read data from the two csv files
    Person = sc.textFile(aboxPath + "Person" + "/")
    hasAlum = sc.textFile(aboxPath + "hasAlumnus" + "/")

    # condition of domain in the WHERE clause
    dom = "<http://www.University0.edu>" 

    # WHERE  hasAlumnus.domain = 'http://www.University0.edu'
    ranHasAlum = hasAlum.filter(lambda x : dom == x.split(",")[0]).map(lambda x : x.split(",")[1]).persist(persistLevel)
    Person.persist(persistLevel)

    ans = ranHasAlum.intersection(Person)
    ans.persist(persistLevel)

    numAns = ans.count()

    # record the end of excuting this query
    end = datetime.datetime.now()
    
    print("**** The number of answers to LUBM query 13 is %i ****" % numAns)
    print("**** The time used for LUBM query 13 is %s " % str(end - start))

    return end - start

def lubm_q14(sc, aboxPath, partitions):
    """
    --Query 14
    SELECT  count (id)
    FROM UndergraduateStudent;
    """
    """
    SELECT ?X
    WHERE {?X rdf:type ub:UndergraduateStudent}
    """
    # record the start time of executing query 6
    start = datetime.datetime.now()

    # read data from related csv file
    UndergraduateStudent = sc.textFile(aboxPath + "UndergraduateStudent" + "/")

    ans = UndergraduateStudent
    ans.persist(persistLevel)

    numAns = ans.count()    
    
    # record the end of excuting this query
    end = datetime.datetime.now()
    
    print("**** The number of answers to LUBM query 14 is %i ****" % numAns)
    print("**** The time used for LUBM query 14 is %s " % str(end - start))

    return end - start

    
if __name__ == "__main__":
    """
    Usage [${aboxPath}] [${partitions}]
    """

    if len(sys.argv) == 1:
        print >> sys.stderr, "Please specify the path of the abox data"
        exit(1)

    aboxName = sys.argv[1]
    aboxPath = sys.argv[2]
    partitions = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    print("**** GIVEN VARIABLES ****")
    print("aboxName: ", aboxName)
    print("aboxPath: ", aboxPath)
    print("partitions: ", partitions)

    # define a spark context
    conf = pyspark.SparkConf().setAppName("Sqowl2-PySpark: LUBM Query Processing for " + aboxName)
    sc = pyspark.SparkContext(conf = conf)

    # process lubm queries
    print("**** PERFORMANCE REPORT ****")
    #"""
    print("== QUERY 2, 9 AND 4 ==")
    print(str(lubm_q2(sc, aboxPath, partitions)))
    print(str(lubm_q9(sc, aboxPath, partitions)))
    print(str(lubm_q4(sc, aboxPath, partitions)))
    #"""
    """
    print("== QUERY 1, 3, 5, 10, 11 AND 13 ==")
    print(str(lubm_q1(sc, aboxPath, partitions)))
    print(str(lubm_q3(sc, aboxPath, partitions)))
    print(str(lubm_q5(sc, aboxPath, partitions)))
    print(str(lubm_q10(sc, aboxPath, partitions)))
    print(str(lubm_q11(sc, aboxPath, partitions)))    
    print(str(lubm_q13(sc, aboxPath, partitions)))
    """
    """
    print("== QUERY 6 AND 14 ==")
    print(str(lubm_q6(sc, aboxPath, partitions)))
    print(str(lubm_q14(sc, aboxPath, partitions)))
    """
    """
    print("== QUERY 7 AND 12 ==")
    print(str(lubm_q7(sc, aboxPath, partitions)))
    print(str(lubm_q12(sc, aboxPath, partitions)))
    """
    """
    print("== QUERY 8 ==")
    print(str(lubm_q8(sc, aboxPath, partitions)))
    """
