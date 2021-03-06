import random
class RegisterSystem:

    def __init__(self, offeredCourses, currentSemesterOfSystem,advisor):
        self.offeredCourses = offeredCourses
        self.currentSemester = currentSemesterOfSystem
        self.advisor = advisor
        if self.currentSemester == "fall":
            self.semesterCode = 1
        else:
            self.semesterCode = 0
        

    def getGradedCourses(self, student):
        # passed Courses and their code versions for easier use.
        passedCourses = []
        passedCoursesCodes = []

        # failed Courses and their code versions for easier use.
        failedCourses = []
        failedCoursesCodes = []

        # reason for reverse operation: if a student takes x course in 1st semester and fails,
        # takes the same x course in 2nd semester and passes, transcript will record it as
        # 1st sem: FF, 2nd sem: Pass. Therefore we read the transcript reversed so we find out
        # if student passed the course at last.
        for i in reversed(student.transcript.transcriptList):
            for j in i[1]:
                if "FF" in j[1] and j[0].courseCode.code not in passedCoursesCodes \
                        and j[0].courseCode.code not in failedCoursesCodes:
                    failedCourses.append(j[0])
                    failedCoursesCodes.append(j[0].courseCode.code)
                else:
                    passedCourses.append(j[0])
                    passedCoursesCodes.append(j[0].courseCode.code)

        return passedCourses, passedCoursesCodes, failedCourses, failedCoursesCodes

    def getAvailableCourses(self, student):

        #get all taken courses by the student whether it is passed or failed.
        allTakenCourses = []
        allTakenCoursesCodes = []
        for i in student.transcript.transcriptList:
            for j in i[1]:
                if j[0].courseCode.code not in allTakenCoursesCodes:
                    allTakenCourses.append(j[0])
                    allTakenCoursesCodes.append(j[0].courseCode.code)

        #filter all taken classes as passed or failed.
        passedCourses, passedCoursesCodes, failedCourses, failedCoursesCodes = self.getGradedCourses(student)

        #return value to student for non-elective courses' list
        semesterCourses = []

        #all courses except electives.
        mandatoryCourses = []
        for i in self.offeredCourses:
            if i.semester <= '8':
                mandatoryCourses.append(i)

        #non-elective courses which are not taken past year(s) are offered to take in this year.
        #ex: ISG101 course is not taken before, so student can take it this year.
        notTakenCourses = []
        for i in mandatoryCourses:
            if int(i.semester) < int(student.semester) and i.courseCode.code not in allTakenCoursesCodes:
                if "NTE" not in i.courseCode.code\
                        and "FTE" not in i.courseCode.code\
                        and "TE" not in i.courseCode.code\
                        and "UE" not in i.courseCode.code:
                    notTakenCourses.append(i)

        #chooosing the non-elective courses that can be taken in the student's current semester.
        for i in mandatoryCourses:
            if i.semester == str(student.semester):
                if "NTE" not in i.courseCode.code \
                        and "FTE" not in i.courseCode.code \
                        and "TE" not in i.courseCode.code \
                        and "UE" not in i.courseCode.code:
                    semesterCourses.append(i)

        #checking for prerequisites in the selected courses. If the student failed it's prerequisite
        #before, student must take it again.
        for i in semesterCourses:
            if i.prerequisites:
                for k in failedCourses:
                    if i.prerequisites.courseCode.code == k.courseCode.code:
                        semesterCourses.remove(i)
                        semesterCourses.append(k)
                        print("Student " + student.studentID.fullID + " couldn't pick " + i.courseCode.code +
                              " course because it requires " + k.courseCode.code + " course.")

                for k in notTakenCourses:
                    if i.prerequisites.courseCode.code == k.courseCode.code:
                        semesterCourses.remove(i)
                        semesterCourses.append(k)
                        print("Student " + student.studentID.fullID + " couldn't pick " + i.courseCode.code +
                              " course because it requires " + k.courseCode.code + " course.")

        semesterCoursesCodes = []
        for i in semesterCourses:
            semesterCoursesCodes.append(i.courseCode.code)

        for i in failedCourses:
            if i.courseCode.code not in semesterCoursesCodes:
                semesterCourses.append(i)
                semesterCoursesCodes.append(i.courseCode.code)

        for i in notTakenCourses:
            if i.courseCode.code not in semesterCoursesCodes:
                semesterCourses.append(i)
                semesterCoursesCodes.append(i.courseCode.code)


        #detect current semester that system is operating on and remove courses that aren't belong to this semester.
        filteredSemesterCourses = []
        filteredSemesterCoursesCodes = []
        for i in semesterCourses:
            if self.currentSemester == "fall":
                if int(i.semester) % 2 != 0:
                    filteredSemesterCourses.append(i)
                    filteredSemesterCoursesCodes.append(i.courseCode.code)
            else:
                if int(i.semester) % 2 == 0:
                    filteredSemesterCourses.append(i)
                    filteredSemesterCoursesCodes.append(i.courseCode.code)

        for i in semesterCourses:
            if i.courseCode.code not in filteredSemesterCoursesCodes:
                print(i.courseCode.code + " can not be taken in " + self.currentSemester + " semester.")

        #############################################################################################
        #### ELECTIVE COURSES
        # calculation of count of all elective courses which are taken by the student.
        takenNTEandUE = 0
        takenFTE = 0
        takenTE = 0
        for i in allTakenCourses:
            if int(i.semester) == 11:
                takenNTEandUE += 1
            elif int(i.semester) == 10:
                takenFTE += 1
            elif int(i.semester) == 9:
                takenTE += 1

        # calculation of the maximum count of elective courses that can be chosen according to student's semester.
        # (independent from past year selections. here we assume that student never chose an elective course.)
        countOfNTEandUE = 0
        countOfFTE = 0
        countOfTE = 0
        if int(student.semester) < 7:
            countOfNTEandUE = 1
        elif int(student.semester) < 8:
            countOfNTEandUE = 2
            countOfTE = 1
        elif int(student.semester) >= 8:
            countOfNTEandUE = 3
            countOfTE = 4
            countOfFTE = 1

        # calculating how many courses to take from each elective list
        countOfNTEandUEToTake = countOfNTEandUE - takenNTEandUE
        countOfTEToTake = countOfTE - takenTE
        countOfFTEToTake = countOfFTE - takenFTE

        # list of offered elective courses
        courseNTEandUE = []
        courseFTE = []
        courseTE = []
        for i in self.offeredCourses:
            if i.semester == "11" and i.courseCode.code not in allTakenCoursesCodes:
                courseNTEandUE.append(i)
            elif i.semester == "10" and i.courseCode.code not in allTakenCoursesCodes:
                courseFTE.append(i)
            elif i.semester == "9" and i.courseCode.code not in allTakenCoursesCodes:
                courseTE.append(i)

        # CourseCode: Semester-Count
        # NTE: 2-1, 8-1
        # TE: 7-1, 8-3
        # FTE: 8-1
        # UE: 7-1.
        student.courseNTEandUE = courseNTEandUE
        student.courseFTE = courseFTE
        student.courseTE = courseTE
        student.countOfNTEandUEToTake = countOfNTEandUEToTake
        student.countOfTEToTake = countOfTEToTake
        student.countOfFTEToTake = countOfFTEToTake
        student.availableCourses = filteredSemesterCourses


    def show(self, nonElectiveCourseList, student):
        #student.transcript.show()
        print("-----------\n" + student.firstName + " " + student.lastName + " " + str(student.semester) + ". SEMESTER\n"
            "Courses that can be taken this semester are:")
        for i in nonElectiveCourseList:
            print(i.courseCode.code + " " + i.courseName + " " + i.semester + ". semester course")