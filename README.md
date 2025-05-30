# SD

Instructions for running the tests:

<!-- TODO requirements.txt -->

## XMLRPC

Execute directly the `insultDemo.py`, `filterDemo.py`, or `insultStress.py` script.
Requires open tcp port {8080..8082}.

## PyRO

Insult service demo:

```bash
python3 -m Pyro4.naming &
python3 ./PRAC1/PyRO/insult_service/server.py &
python3 ./PRAC1/PyRO/clients/insult_service_client_pyro.py
```

Filter service demo:

```bash
python3 -m Pyro4.naming &
python3 ./PRAC1/PyRO/insult_filter/server.py &
python3 ./PRAC1/PyRO/clients/insult_filter_client_pyro.py
```

Insult service:

```
python3 ./PRAC1/PyRO
python3 ./PRAC1/PyRO/insult_service
python3 ./PRAC1/PyRO/insult_service/model.py
python3 ./PRAC1/PyRO/insult_service/server.py
python3 ./PRAC1/PyRO/insult_service/insult_service_server_distributed.py
python3 ./PRAC1/PyRO/insult_service/__pycache__
python3 ./PRAC1/PyRO/insult_service/__pycache__/model.cpython-313.pyc
python3 ./PRAC1/PyRO/tests
python3 ./PRAC1/PyRO/tests/performance_test_insult_service.py
python3 ./PRAC1/PyRO/tests/performance_test_insult_filter.py
python3 ./PRAC1/PyRO/tests/performance_test.py
python3 ./PRAC1/PyRO/tests/test_services.py
python3 ./PRAC1/PyRO/clients
python3 ./PRAC1/PyRO/clients/insult_filter_client_pyro.py
python3 ./PRAC1/PyRO/clients/insult_service_client_pyro.py
python3 ./PRAC1/PyRO/insult_filter
python3 ./PRAC1/PyRO/insult_filter/model.py
python3 ./PRAC1/PyRO/insult_filter/server.py
python3 ./PRAC1/PyRO/insult_filter/__pycache__
python3 ./PRAC1/PyRO/insult_filter/__pycache__/model.cpython-313.pyc
python3 ./PRAC1/PyRO/insult_filter/filter_server_distributed.py
python3 ./PRAC1/PyRO/load_balancer.py
```

## Redis

Execute directly the `insultDemo.py`, `filterDemo.py`, or `filterStress.py` script.
Requires running Redis server on the default port.

## RabbitMQ

.
./PRAC1
./PRAC1/RabbitMQ
./PRAC1/RabbitMQ/insult_service
./PRAC1/RabbitMQ/insult_service/model.py
./PRAC1/RabbitMQ/insult_service/server.py
./PRAC1/RabbitMQ/insult_service/insult_service.py
./PRAC1/RabbitMQ/tests
./PRAC1/RabbitMQ/tests/test_insult_service.py
./PRAC1/RabbitMQ/tests/plot_results.py
./PRAC1/RabbitMQ/tests/performance_test.py
./PRAC1/RabbitMQ/tests/multi_run_performance_test.py
./PRAC1/RabbitMQ/tests/test_insult_filter.py
./PRAC1/RabbitMQ/tests/performance_test_rabbitmq_node.py
./PRAC1/RabbitMQ/clients
./PRAC1/RabbitMQ/clients/insult_service_client_rabbit.py
./PRAC1/RabbitMQ/clients/subscribe_insults_client.py
./PRAC1/RabbitMQ/clients/send_text_client.py
./PRAC1/RabbitMQ/clients/get_insults_client.py
./PRAC1/RabbitMQ/clients/get_results_client.py
./PRAC1/RabbitMQ/clients/add_insult_client.py
./PRAC1/RabbitMQ/insult_filter
./PRAC1/RabbitMQ/insult_filter/insult_filter_service.py
./PRAC1/RabbitMQ/insult_filter/model.py
./PRAC1/RabbitMQ/insult_filter/server.py
./PRAC1/redis
./PRAC1/redis/filterDemo.py
./PRAC1/redis/filterService.py
./PRAC1/redis/insultService.py
./PRAC1/redis/filterStress.py
./PRAC1/redis/insultDemo.py
./PRAC1/xmlrpc
./PRAC1/xmlrpc/filterDemo.py
./PRAC1/xmlrpc/filterService.py
./PRAC1/xmlrpc/insultService.py
./PRAC1/xmlrpc/insultStress.py
./PRAC1/xmlrpc/insultDemo.py
./PRAC1/RabbitMQ_stateless
./PRAC1/RabbitMQ_stateless/insult_service
./PRAC1/RabbitMQ_stateless/insult_service/add_insult.py
./PRAC1/RabbitMQ_stateless/insult_service/get_insults.py
./PRAC1/RabbitMQ_stateless/insult_service/insult_me.py
./PRAC1/RabbitMQ_stateless/insult_service/insult_subscriber.py
./PRAC1/RabbitMQ_stateless/insult_service/insult_server.py
./PRAC1/RabbitMQ_stateless/tests
./PRAC1/RabbitMQ_stateless/tests/performance_test_static.py
./PRAC1/RabbitMQ_stateless/tests/performance_test_1node.py
./PRAC1/RabbitMQ_stateless/tests/plot_metrics.py
./PRAC1/RabbitMQ_stateless/tests/plot_static_metrics.py
./PRAC1/RabbitMQ_stateless/filter_service
./PRAC1/RabbitMQ_stateless/filter_service/filter_server.py
./PRAC1/RabbitMQ_stateless/filter_service/filter_text.py
./PRAC1/RabbitMQ_stateless/filter_service/get_filtered_texts.py
./PRAC1/RabbitMQ_stateless/insults.txt
