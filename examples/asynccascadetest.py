import cv2
import asyncio
import time

async def waiter(event):
    print("Waiting")
    await event.wait()
    print("Going")


async def main():
    image_1 = cv2.imread("D:\Desktop\Dissertation\images\can_bedroom_shelf_2\\vott-csv-export\image00.jpg")
    image_2 = cv2.imread("D:\Desktop\Dissertation\images\can_bedroom_shelf\\vott-csv-export\image01.jpg")

    can = "D:\Desktop\Dissertation\images\cas\can_cas\cascade404020s.xml"
    cereal = "D:\Desktop\Dissertation\images\cas\cereal_cas\cascade.xml"

    event = asyncio.Event()
    waiter_task = asyncio.create_task(waiter(event))
    if not event.is_set():
        event.set()
    t_1 = asyncio.create_task(recognise(can, image_1, 1, event))
    t_2 = asyncio.create_task(recognise(cereal, image_2, 2, event))
    a = await asyncio.gather(t_1, t_2)
    print(a)
    print("{0}, {1}".format(a[0], a[1]))


async def recognise(casc, image, id, event):
    if event.is_set():
        event.clear()
    print(id)
    print(f"started at {time.strftime('%X')}")
    rec = cv2.CascadeClassifier(casc)
    match = rec.detectMultiScale3(image, 1.05, 5, outputRejectLevels=True)
    print("done")
    event.set()
    return match


asyncio.run(main())
