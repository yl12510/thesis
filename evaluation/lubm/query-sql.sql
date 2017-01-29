--Query 1
SELECT COUNT (id)
FROM GraduateStudent
JOIN takesCourse
ON GraduateStudent.id = takesCourse.domain
WHERE takesCourse.range = 'http://www.Department0.University0.edu/GraduateCourse0'


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
AND undergraduateDegreeFrom.range = University.id


--Query 3
SELECT id
FROM Publication
JOIN publicationAuthor
ON Publication.id = publicationAuthor.domain
WHERE publicationAuthor.range = 'http://www.Department0.University0.edu/AssistantProfessor0'


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
AND   Professor.id = telephone.domain


--Query 5
SELECT count (Person.id)
FROM Person, memberOf
WHERE Person.id = memberOf.domain
AND memberOf.range = 'http://www.Department0.University0.edu'


--Query 6
SELECT  count (id)
FROM Student


--Query 7
SELECT count (Student.id)
FROM   Student, Course, takesCourse, teacherOf
WHERE  Student.id = takesCourse.domain
AND    takesCourse.range = Course.id
AND    teacherOf.range = Course.id
AND    teacherOf.domain = 'http://www.Department0.University0.edu/AssociateProfessor0'



--Query 8
SELECT count (Student.id)
FROM   Student, Department, memberOf, subOrganizationOf, emailAddress
WHERE  Student.id = memberOf.domain
AND    Department.id = memberOf.range
AND    Department.id = subOrganizationOf.domain
AND    subOrganizationOf.range = 'http://www.University0.edu'
AND    Student.id = emailAddress.domain


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
AND    takesCourse.range = Course.id

--Query 10 
SELECT count (Student.id)
FROM   Student, takesCourse
WHERE  Student.id = takesCourse.domain 
AND    takesCourse.range = 'http://www.Department0.University0.edu/GraduateCourse0'

--Query 11 
SELECT count (ResearchGroup.id)
FROM   ResearchGroup, subOrganizationOf 
WHERE  ResearchGroup.id = subOrganizationOf.domain 
AND    subOrganizationOf.range = 'http://www.University0.edu'

--Query 12
SELECT count (Chair.id)
FROM   Chair, worksFor, subOrganizationOf
WHERE  Chair.id = worksFor.domain 
AND    worksFor.range = subOrganizationOf.domain 
AND    subOrganizationOf.range = 'http://www.University0.edu'

--Query 13 
SELECT count (Person.id)
FROM   Person, hasAlumnus 
WHERE  hasAlumnus.domain = 'http://www.University0.edu'
AND    hasAlumnus.range = Person.id 

--Query 14
SELECT count (id)
FROM UndergraduateStudent
