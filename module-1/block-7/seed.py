import os
from peewee import Model, PostgresqlDatabase, CharField, IntegerField, ForeignKeyField

db_user = os.environ.get('POSTGRES_USER')
db_password = os.environ.get('POSTGRES_PASSWORD')
db_name = os.environ.get('POSTGRES_DB')
student_name = os.environ.get('STUDENT_NAME')

db = PostgresqlDatabase(
    db_name,
    user=db_user,
    password=db_password,
    host='db',
    port=5432
)

class BaseModel(Model):
    class Meta:
        database = db

class Student(BaseModel):
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    email = CharField(max_length=100, unique=True)
    enrollment_year = IntegerField()
    
    class Meta:
        table_name = 'students'

class Course(BaseModel):
    name = CharField(max_length=100)
    credits = IntegerField()
    
    class Meta:
        table_name = 'courses'

class Enrollment(BaseModel):
    student = ForeignKeyField(Student, backref='enrollments', column_name='student_id')
    course = ForeignKeyField(Course, backref='enrollments', column_name='course_id')
    grade = IntegerField(null=True)
    
    class Meta:
        table_name = 'enrollments'

def main():
    db.connect()
    
    db.drop_tables([Enrollment, Course, Student])
    db.create_tables([Student, Course, Enrollment])

    name_parts = student_name.split(' ', 1) if student_name else [""]
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    with db.atomic():
        students_data = [
            {'first_name': first_name, 'last_name': last_name, 'email': f'{first_name.lower()}@uni.edu', 'enrollment_year': 2023},
            {'first_name': 'Olena', 'last_name': 'Kovalenko', 'email': 'olena@uni.edu', 'enrollment_year': 2022},
            {'first_name': 'Ivan', 'last_name': 'Franko', 'email': 'ivan@uni.edu', 'enrollment_year': 2021},
            {'first_name': 'Lesya', 'last_name': 'Ukrainka', 'email': 'lesya@uni.edu', 'enrollment_year': 2023},
            {'first_name': 'Mykhailo', 'last_name': 'Hrushevskyi', 'email': 'mykhailo@uni.edu', 'enrollment_year': 2020}
        ]
        Student.insert_many(students_data).execute()

        courses_data = [
            {'name': 'Calculus', 'credits': 5},
            {'name': 'Python Programming', 'credits': 4},
            {'name': 'Databases', 'credits': 4},
            {'name': 'Algorithms and Data Structures', 'credits': 6}
        ]
        Course.insert_many(courses_data).execute()

        enrollments_data = [
            {'student_id': 1, 'course_id': 1, 'grade': 95},
            {'student_id': 1, 'course_id': 2, 'grade': 100},
            {'student_id': 2, 'course_id': 3, 'grade': 85},
            {'student_id': 2, 'course_id': 4, 'grade': 90},
            {'student_id': 3, 'course_id': 1, 'grade': 75},
            {'student_id': 3, 'course_id': 2, 'grade': 88},
            {'student_id': 4, 'course_id': 3, 'grade': 92},
            {'student_id': 4, 'course_id': 4, 'grade': 98},
            {'student_id': 5, 'course_id': 1, 'grade': 60},
            {'student_id': 5, 'course_id': 4, 'grade': 70}
        ]
        Enrollment.insert_many(enrollments_data).execute()

    s_count = Student.select().count()
    c_count = Course.select().count()
    e_count = Enrollment.select().count()

    db.close()

    print("============================================")
    print(f" Seed script — {student_name}")
    print("============================================\n")
    print(f"Connecting to database {db_name}...")
    print("Tables created.")
    print(f"Added {s_count} students.")
    print(f"Added {c_count} courses.")
    print(f"Added {e_count} enrollments.")
    print("---")
    print(f"Summary ({student_name}):")
    print(f"  students:    {s_count}")
    print(f"  courses:     {c_count}")
    print(f"  enrollments: {e_count}")
    print("Done!")

if __name__ == '__main__':
    main()