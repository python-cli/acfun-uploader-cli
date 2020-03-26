remote := "aliyun"
remote_path := "~/projects/acfun-uploader-cli"

help:
    @echo "This cli tool is used for uploading videos to acfun site."

# run all the upload tasks endlessly
run:
    python main.py

# publish project to remote gcp instance not including git and log files
publish:
    rsync -arv --delete --exclude .git --exclude '*.log*' . {{remote}}:{{remote_path}}
