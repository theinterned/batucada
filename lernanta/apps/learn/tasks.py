import requests

from celery.task import Task


class UpdateCourseTask(Task):
    name = 'learn.tasks.UpdateCourseTask'

    def run(self, course_url, course_data_url, **kwargs):
        # get course data from course data URL
        try: 
            results = request.post(course_data_url)
        except:
            # could not fetch course data, verify that course still exists?
            pass

        # update course data in db
