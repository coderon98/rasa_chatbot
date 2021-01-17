# Extend the official Rasa SDK image
FROM rasa/rasa-sdk:2.0.0

# Use subdirectory as working directory
WORKDIR /app

# Change back to root user to install dependencies
USER root

# Install extra requirements for actions code
RUN python3 -m pip install --upgrade pip \
&& pip3 install pandas \
&& pip3 install torch \
&& pip3 install pdfminer \
&& pip3 install elasticsearch

# Copy actions folder to working directory
COPY ./actions /app/actions

# By best practices, don't run the code with root user
USER 1001



