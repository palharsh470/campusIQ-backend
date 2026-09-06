from django.contrib import admin
from .models import Program, ClassGroup, Enrollment, TeacherAssignment

admin.site.register(Program)
admin.site.register(ClassGroup)
admin.site.register(Enrollment)
admin.site.register(TeacherAssignment)
