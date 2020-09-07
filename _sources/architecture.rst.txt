====================
Overall architecture
====================

A simple representation of the architectore would be the producer -> kafka ->
consumer -> postgres, e.g.::


                              +---------------+
     +--------------+         |     aiven     |
     |   checker    |+-------->     kafka     |
     +--------------+         +-------+-------+
                                      |
                                      |
                                      |
                              +-------v-------+
                              |   consumer    |
                              +-------+-------+
                                      |
                                      |
                                      |
                              +-------v-------+
                              |    aiven      |
                              |  PostgreSQL   |
                              +---------------+




A more detailed graph includes the inner workings of the services. The site
checker module creates an asyncio task running periodically for every site in
the config, feeding an asyncio [mpsc] Queue from which the consumer is
forwarding messages in the kafka topic specified in the configuration::


     + periodical asyncio tasks ----+
     |                              |
     |                              |
     |       +-------------+        |
     |       | example.com +--------+---------+
     |       +-------------+        |    +----v----+       +------------+
     |         +-----------+        |    | asyncio |       |            |
     |         | aiven.com +--------+---->  Queue  +------->  producer  |
     |         +-----------+        |    +----^----+       |            |
     |        +------------+        |         |            +-----+------+
     |        | google.com +--------+---------+                  |
     |        +------------+        |                            |
     |                              |                            |
     |                              |                            |
     +------------------------------+                            |
                                                                 |
                                                        +--------v---------+
                                                        |                  |
                                                        |   aiven kafka    |
                                                        |                  |
                                                        +--------+---------+
                                                                 |
                             +----------------+                  |
                             |                |                  |
                             |     aiven      |           +------v------+
                             |   PostgreSQL   <-----------+  consumer   |
                             |                |           +-------------+
                             +----------------+



