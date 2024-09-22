# Lab 1: Pastebin Application

This is a simple Pastebin application built with Flask.

## Setup

1. Install Python 3.
2. Install `virtualenv`:
    ```sh
    pip install virtualenv
    ```
3. Create and activate a virtual environment:
    ```sh
    virtualenv venv
    source venv/bin/activate
    ```

    On Windows, run:

    ```
    .venv\Scripts\activate
    ```

4. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Run

To run the application, use the following command:
```sh
flask --env-file env_file run
```
**OR**

```
flask -e env_file run
```
## Testing

To run the tests, use the following command:
```sh
pytest
```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## Security

For more details on secure coding practices, please refer to the [OWASP Developer Guide](https://owasp.org/www-project-top-ten/) and [SECURITY.md](SECURITY.md).

## Additional Documentation

- [INSTRUCTIONS.md](INSTRUCTIONS.md)
