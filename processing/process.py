
from load_configs import load_log_conf

LOGGER = load_log_conf()


def process_jobs(data, previous_data):
    """
    Updates
        num_jobs: int,
        average_salary: int

    """
    if not data:
        return
    total_jobs = previous_data['num_jobs'] + len(data)
    previous_salary = previous_data['average_salary']
    for job in data:
        LOGGER.debug(f"Processing job event: {job['trace_id']}")
        previous_salary += job['salary']

    new_average_salary = previous_salary // total_jobs

    previous_data['num_jobs'] = total_jobs
    previous_data['average_salary'] = new_average_salary


def process_applications(data, previous_data):
    """
    Updates
        num_applications: int,
        max_experience: int

    """
    if not data:
        return
    total_applications = previous_data['num_applications'] + len(data)
    mx = 0
    for application in data:
        mx = max(mx, application['years_of_experience'])
        LOGGER.debug(
            f"Processing application event: {application['trace_id']}")

    max_experience = max(previous_data['max_experience'], mx)
    previous_data['num_applications'] = total_applications
    previous_data['max_experience'] = max_experience
