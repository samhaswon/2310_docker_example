# 2310 Docker Example

This project highlights how Docker can be useful in the deployment of an application.

## What is it?

This is a rather basic note-taking server that uses [MongoDB](https://www.mongodb.com/) in a separate container to store the user's data. Over all, this repo highlights the benefits of Docker with:

- Containerization of the application with all of its dependencies

    - Smaller than doing so with a virtual machine

- Building an application stack with [Docker Compose](./docker-compose.yml)

- Docker networking: In conjunction with Docker Compose, containers in the application stack can reference each other by name. Here, the `notes` container can reference the database container by the name `mongo`.

## Container

The container can be built with:

```shell 
docker build -t notes .
```

or

```shell 
docker-compose build
```

---

To bring up the stack, run:

```shell 
docker-compose up -d
```

---

And stop it with:

```shell
docker-compose stop
```
