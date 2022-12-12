# SEA Coursework Platform

## Overview

SEA Coursework is a platform designed to improve the coursework experience for teacher and students from a specific class at a university in Taiwan. With a range of features and benefits, the platform offers a unique and easy-to-use solution for managing and completing coursework assignments.

## Features

Some of the key features of the platform include:

-   Easy registration using a student ID
-   School email addresses verification to ensure that students are legitimate
-   Teacher can create coursework and assignments, each with its own deadline
-   Students can upload their homework before the deadline
-   A memo text area for students to write down their thoughts and notes on assignments
-   Submission status is displayed after the deadline, allowing teacher to track student progress easily
-   Teaching assistants have the authority to assist teachers by creating assignments, confirming or denying students' requests to join coursework, etc

## Technologies

The project uses the following technologies:

-   Python with the Django web framework
-   JavaScript for client-side scripting
-   HTML for structuring the content
-   CSS with the Bootstrap framework for styling and layout

These technologies enable the development of a dynamic and responsive web application that can serve a variety of purposes.

## How to Run the Project

1. Install the required python libraries by running the following command:

```python
pip install -r requirements.txt
```

2. Open the .env-sample file and you will see the following settings:

```
export SECRET_KEY="<PUT YOUR KEY HERE>"
export EMAIL_FROM_USER="<PUT YOUR EMAIL HERE>"
export EMAIL_HOST_PASSWORD="<PUT YOUR EMAIL PASSWORD HERE>"
```

The `SECRET_KEY` is a critical component for any Django installation, as it is used for cryptographic signing. Django will refuse to start if the `SECRET_KEY` is not set, so it is essential to configure this key properly.

The `EMAIL_FROM_USER` is the email address that is used to send verification email to students after they register on the platform.

The `EMAIL_HOST_PASSWORD` is the password for the `EMAIL_FROM_USER` email account, which is used to authenticate and authorize the email server to send messages on behalf of the `EMAIL_FROM_USER`.

3. Fill in the values for the `SECRET_KEY`, `EMAIL_FROM_USER`, and `EMAIL_HOST_PASSWORD` in the `.env-sample` file. Then, run the following commands to start the Django development server:

```
source .env-sample
python3 manage.py runserver
```

## Distinctiveness and Complexity

As a former teaching assistant in this class, I had the unfortunate experience of dealing with a student who cheated by stealing another student's assignment and submitting it as their own. This incident occurred when we were using a cloud-based platform where students could see each other's uploaded files. It caused a lot of distress among the students who were affected. In response to this incident, I try to develop this web app, in which students can only see their own uploads when submitting assignments on the platform. This ensures that each student's work is kept private and that only the teacher and teaching assistants have the ability to preview all students' submissions.

A deadline attribute is also implemented on the upload function to ensure that it closes automatically, eliminating the need for teachers or teaching assistants to close it manually. This platform also streamlines the grading process by automating tedious tasks such as automatically organising and renaming submitted files. This saves teaching assistants time and reduces the potential for errors. After the submission deadline, a results page will generate, allowing teachers and teaching assistants to easily view the status of each assignment, making it easy to manage and evaluate student work. Besides, the system will automatically package all necessary files into a compressed file, and the teacher will be able to download the file by clicking the download button on the preview results page.
