import asyncio
import enum
import random
from dataclasses import dataclass

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from dataclasses_avroschema import AvroModel


class FavoriteColor(enum.Enum):
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


@dataclass
class UserModel(AvroModel):
    "An User"
    name: str
    age: int
    favorite_colors: FavoriteColor = FavoriteColor.BLUE
    country: str = "Argentina"
    address: str = None

    class Meta:
        namespace = "User.v1"
        aliases = ["user-v1", "super user"]


async def consume(loop, total_events=10):
    consumer = AIOKafkaConsumer(
        "my_topic", "my_other_topic", loop=loop, bootstrap_servers="localhost:9092", group_id="my-group"
    )
    # Get cluster layout and join group `my-group`
    await consumer.start()
    run_consumer = True

    while run_consumer:
        try:
            # Consume messages
            async for msg in consumer:
                print(f"Message received: {msg.value} at {msg.timestamp}")

                user = UserModel.deserialize(msg.value)
                print(f"Message deserialized: {user}")
        except KeyboardInterrupt:
            # Will leave consumer group; perform autocommit if enabled.
            await consumer.stop()
            print("Stoping consumer...")
            run_consumer = False


async def send(loop, total_events=10):
    producer = AIOKafkaProducer(loop=loop, bootstrap_servers="localhost:9092")
    # Get cluster layout and initial topic/partition leadership information
    await producer.start()

    for event_number in range(1, total_events + 1):
        # Produce message
        print(f"Sending event number {event_number}")

        user = UserModel(
            name=random.choice(
                [
                    "Juan",
                    "Peter",
                    "Michael",
                    "Moby",
                    "Kim",
                ]
            ),
            age=random.randint(1, 50),
        )

        # create the message
        message = user.serialize()

        await producer.send_and_wait("my_topic", message)
        # sleep for 2 seconds
        await asyncio.sleep(2)
    else:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()
        print("Stoping producer...")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    tasks = asyncio.gather(send(loop), consume(loop))

    loop.run_until_complete(tasks)
