def test_subscription():
    from geoffrey.subscription import Subscription
    return Subscription(filter_func=lambda x: True)


def test_subscription_put(loop):
    from geoffrey.subscription import Subscription

    def only_str(data):
        return type(data) == str

    subscription = Subscription(filter_func=only_str)

    assert subscription.qsize() == 0
    loop.run_until_complete(subscription.put("good"))
    assert subscription.qsize() == 1
    loop.run_until_complete(subscription.put(15))
    assert subscription.qsize() == 1
