# After copying your project files
COPY . /usr/src/app/

# Copy the entrypoint script
COPY entrypoint.sh /usr/src/app/entrypoint.sh

# Give execution rights on the entrypoint script
RUN chmod +x /usr/src/app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
