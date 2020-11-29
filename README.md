```
login - Авторизация. POST с JSON {'login': 'test', 'password': 'rosseti12'} возвращает token если ок, ошибку если нет. 
logout - Деавторизация. POST с заголовком token.

get_profile - Получить свой профиль. GET с заголовком token.
get_favorits - Получить избранные топики. GET с заголовком token.
change_password - Смена пароля. POST с JSON {'password': 'blablabla', 'password_repeat': 'blablabla'} и с заголовком token.

get_states - Получить все статусы для форумов. GET с заголовком token.

get_topics - Получить топики. Возвращает все топики с 5 форумами. GET с опциональными параметрами limit = 5, interestings = 0 и заголовком token. Если interestings = 0, то возвращает все топики с количеством форумов равному limit, если interestings = 1, то возвращает только заинтересованные топики с количеством форумов равному limit.
get_topic - Получить топик.Возвращает один топик с 20 форумами. GET с обязательным параметром topic_id и опциональными offset и limit, и заголовком token. Возвращает один топик с limit форумами начиная с offset.

set_intrests - Добавить топики в предпочтения. POST с JSON {'interests_ids': [1, 2, 3]} и с заголовком token, где числа это id топиков. Возвращает массив interests_ids c добавленными топиками если все ок, ошибку если нет. 
get_interests - Получить список топиков в предпочтениях. GET с заголовком token.

get_forum - Получить свой профиль. GET c обязательным параметром forum_id с опциональыми offset и limit, и заголовком token. Возвращает форум с limit комментариями начиная с offset.
create_forum - Создать форум. POST с JSON {'topic_id': 1, 'status_id': 1, 'head': 'Заголовок форума', 'body': 'Тело форума'} и с заголовком token. Возвращает forum_id форума если все ок, ошибку если нет.
favorite_forum - Добавить форум в избранные. POST с JSON {'forum_id': 1} и с заголовком token. Возвращает favorite_id если все ок, ошибку если нет.
unfavorite_forum - Убрать форум из избранных. POST с JSON {'forum_id': 1} и с заголовком token. Возвращает favorite_id если все ок, ошибку если нет.

upvote_forum - Проголосовать наверх за форум. POST с JSON {'forum_id': 1} и заголовком token. Возвращает vote_id если все ок, ошибку если нет. 
downvote_forum - Проголосовать вниз за форум. POST с JSON {'forum_id': 1} и заголовком token. Возвращает vote_id если все ок, ошибку если нет.
unvote_forum - Убрать голос за форум. POST с JSON {'forum_id': 1} и заголовком token. Возвращает vote_id если все ок, ошибку если нет.

create_comment - Создать коммент в форуме POST с JSON {'forum_id': 1, 'message': 'Текст комментария'} и с заголовком token. Возвращает id комментария если все ок, ошибку если нет.

get_users - Возвращает всех пользователей. GET с заголовком token.
get_users/<str:search> - Возвращает пользователей, у которых с search совпадает фамилия, имя, отчетство, должность, организация, структурное подразделение, должность. GET с заголовком token.

get_chats - Получить список чатов. Возвращает список ранее созданных чатов. GET с заголовком token.
get_chat/<int:user_id>/<int:user_id> - Получить либо создать чат с пользователем. GET с заголовком token.

send_message - Отправить сообщение пользователю. POST с JSON {'chat_id': 1, text: 'Текст'} и с заголовком token. Возвращает message_id если все ок, ошибку если нет
```
