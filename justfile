remote := "aliyun"
remote_path := "~/projects/acfun-uploader-cli"

help:
    @echo "This cli tool is used for uploading videos to acfun site."

# run all the upload tasks endlessly
run:
    python main.py

# publish project to remote gcp instance not including git and log files
publish:
    rsync -arv --delete --exclude .git --exclude '*.log*' --exclude '*.pyc'  --exclude '__pycache__' . {{remote}}:{{remote_path}}
