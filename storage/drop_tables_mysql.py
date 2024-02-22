from models import JobApplication, JobListing

from create_database import drop_table


drop_table(JobApplication)
drop_table(JobListing)
