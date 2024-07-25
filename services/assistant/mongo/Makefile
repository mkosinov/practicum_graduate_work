include .env

mongo-create-shards:
	# Создаем кластер из 3-х конфигурационных нод
	docker exec -it ${MONGOCFG1} bash -c 'echo "rs.initiate({_id: \"mongors1conf\", configsvr: true, members: [{_id: 0, host: \"${MONGOCFG1}\"}, {_id: 1, host: \"${MONGOCFG2}\"}, {_id: 2, host: \"${MONGOCFG3}\"}]})" | mongosh'
	# Создаем первый шард из 3 реплик
	docker exec -it ${MONGORS1N1} bash -c 'echo "rs.initiate({_id: \"mongors1\", members: [{_id: 0, host: \"${MONGORS1N1}\"}, {_id: 1, host: \"${MONGORS1N2}\"}, {_id: 2, host: \"${MONGORS1N3}\"}]})" | mongosh'
	# Создаем второй шард из 3 реплик
	docker exec -it ${MONGORS2N1} bash -c 'echo "rs.initiate({_id: \"mongors2\", members: [{_id: 0, host: \"${MONGORS2N1}\"}, {_id: 1, host: \"${MONGORS2N2}\"}, {_id: 2, host: \"${MONGORS2N3}\"}]})" | mongosh'
	@sleep 20

mongo-config: mongo-create-shards
	# Добавляем первый шард к маршрутизатору 1
	docker exec -it ${MONGOS1} bash -c 'echo "sh.addShard(\"mongors1/${MONGORS1N1}\")" | mongosh'
	# Добавляем второй шард к маршрутизатору 2
	docker exec -it ${MONGOS2} bash -c 'echo "sh.addShard(\"mongors2/${MONGORS2N1}\")" | mongosh'
	# Смотрим результат выполнения команд
	docker exec -it ${MONGOS1} bash -c 'echo "sh.status()" | mongosh'
	# Создаем БД
	docker exec -it ${MONGORS1N1} bash -c 'echo "use ${MONGO_DB_NAME}" | mongosh'
	# Включаем шардирование для БД
	docker exec -it ${MONGOS1} bash -c 'echo "sh.enableSharding(\"${MONGO_DB_NAME}\")" | mongosh'
