def test_subscription():
    from geoffrey.subscription import _Subscription
    assert _Subscription(filter_func=lambda x: True)  # pragma: nocover


def test_empty_subscription_means_anything():
    from geoffrey.subscription import _Subscription, ANYTHING
    sub = _Subscription()
    assert sub.filter_func is ANYTHING


def test_anything():
    from geoffrey.subscription import ANYTHING
    assert ANYTHING(False)
    assert ANYTHING(True)
    assert ANYTHING(None)
    assert ANYTHING("")
    assert ANYTHING(0)
    assert ANYTHING([])


def test_subscription_put(loop):
    from geoffrey.subscription import _Subscription

    def only_str(data):
        return type(data) == str

    subscription = _Subscription(filter_func=only_str)

    assert subscription.qsize() == 0
    loop.run_until_complete(subscription.put("good"))
    assert subscription.qsize() == 1
    loop.run_until_complete(subscription.put(15))
    assert subscription.qsize() == 1

def test_subscription_wrapper_generator():
    from geoffrey.subscription import _Subscription, subscription
    #subscription -> wrapper function
    #_Subscription -> The Subscription class

    sub = subscription()

    sub1 = sub()
    sub2 = sub()

    assert isinstance(sub1, _Subscription)
    assert isinstance(sub2, _Subscription)
    assert sub1 is not sub2
