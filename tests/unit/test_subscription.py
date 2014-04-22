

def test_subscription(subscription):
    assert subscription


def test_subscription_put(loop, subscription):

    def only_str(data):
        return type(data) == str

    subscription.add_filter(only_str)

    assert subscription.queue.qsize() == 0
    loop.run_until_complete(subscription.put("good"))
    assert subscription.queue.qsize() == 1
    loop.run_until_complete(subscription.put(15))
    assert subscription.queue.qsize() == 1
