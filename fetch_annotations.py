import time
from h_notify_md import notify_markdown_group_activity, init_logger

# you have to specify values for the variables below on your own;
# MAKE SURE TO NEVER COMMIT THESE VALUES BACK TO GITHUB!!!
hypothesis_api_token = <your-secret-token-here>  # from your user account, typically starts with `6879-`
group_id = <your-secret-group-id>  # from your hypothesis account
group_name = <your-secret-group-name>  # from your hypothesis account
folder = <where markdown notes will be placed> # e.g., Daily Notes folder in Obsidian, can be empty

# you probably don't want to change the lines below
# unless you're abolutely sure what you're doing:
time_delay = 30  # in minutes, wait 30 min to be polite to the hypothesis api
force_log_code = 101 # ensure highest priority


if __name__ == "__main__":
    module_logger = init_logger(name='h_notify', custom_logging=force_log_code)
    # initialize log file and register the started process there:
    module_logger.log(force_log_code, 'Started fetching annotations.')
    while True:
        try:
            module_logger.info(f"Pulling annotations from '{group_name}' group into local file.")
            notify_markdown_group_activity(
                group=group_id,
                groupname=group_name,
                token=hypothesis_api_token,
                folder=folder,
                pickle=group_id,
            )
        except:
            module_logger.exception('Unhandled exception occured.')
        finally:
            module_logger.info('Sleeping.')
            time.sleep(60 * time_delay)  # wait `time_delay` minutes
