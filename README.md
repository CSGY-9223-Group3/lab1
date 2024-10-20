# Lab 1: Pastebin Application

This is a simple Pastebin application built with Flask, containerized using Docker and orchestrated with Docker Compose.

## Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your system.
- [Docker Compose](https://docs.docker.com/compose/install/) installed.

## Setup and Running the Application

### Using Docker Compose

1. **Clone the Repository:**

    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

2. **Create a `.env_file`:**

    Ensure you have a `.env_file` in the project root with the necessary environment variables. Example:

    ```env
    FLASK_APP=pastebin
    FLASK_DEBUG=True
    SECRET_KEY=your_secret_key
    ```
    An example file is also available for demonstration purposes, `.env_file_example`. Flask debug, True for dev and False for otherwise.

3. **Build and Start the Application:**

    ```sh
    docker-compose up --build
    ```

    This command builds the Docker image and starts the Pastebin service. The application will be accessible at [http://localhost:5000](http://localhost:5000).

4. **Stopping the Application:**

    Press `Ctrl+C` in the terminal where `docker-compose` is running, then execute:

    ```sh
    docker-compose down
    ```

### Without Docker (Optional)

If you prefer to run the application without Docker, follow these steps:

1. **Install Python 3.**

2. **Install `virtualenv`:**

    ```sh
    pip install virtualenv
    ```

3. **Create and Activate a Virtual Environment:**

    ```sh
    virtualenv venv
    source venv/bin/activate
    ```

    On Windows, run:

    ```sh
    .venv\Scripts\activate
    ```

4. **Install the Required Dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

5. **Set Environment Variables from `.env_file`:**

    ```sh
    export $(cat .env_file | xargs)
    ```

6. **Run the Flask Application:**

    ```sh
    flask --env-file .env_file run
    ```

## Running the Application

### Using Docker Compose

To start the application with Docker Compose:

```sh
docker-compose up
```


## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## Security

For more details on secure coding practices, please refer to the [OWASP Developer Guide](https://owasp.org/www-project-top-ten/) and [SECURITY.md](SECURITY.md).

## Additional Documentation

- [LAB INSTRUCTIONS.md](INSTRUCTIONS.md)


