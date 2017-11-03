# encoding: UTF-8

from jaqs.util import fileio
from jaqs.trade.tradeapi import TradeApi

def test_trade_api():
    dic = fileio.read_json(fileio.join_relative_path('etc/trade_config.json'))
    address = dic.get("remote.address", None)
    username = dic.get("remote.username", None)
    password = dic.get("remote.password", None)
    if address is None or username is None or password is None:
        raise ValueError("no trade service config available!")
    
    tapi = TradeApi(address, prod_type='jaqs')

    # TradeApi通过回调函数方式通知用户事件。事件包括三种：订单状态、成交回报、委托任务执行状态。

    # 订单状态推送
    def on_orderstatus(order):
        print "on_orderstatus:" #, order
        for key in order:    print "%20s : %s" % (key, str(order[key]))
        print ""


    # 成交回报推送
    def on_trade(trade):
        print "on_trade:"
        for key in trade:    print "%20s : %s" % (key, str(trade[key]))
        print ""

    # 委托任务执行状态推送
    # 通常可以忽略该回调函数
    def on_taskstatus(task):
        print "on_taskstatus:"
        for key in task:    print "%20s : %s" % (key, str(task[key]))
        print ""

    tapi.set_ordstatus_callback(on_orderstatus)
    tapi.set_trade_callback(on_trade)
    tapi.set_task_callback(on_taskstatus)
    
    # 使用用户名、密码登陆， 如果成功，返回用户可用的策略帐号列表
    user_info, msg = tapi.login(username, password)
    print "msg: ", msg
    print "user_info:", user_info

    # 选择使用的策略帐号
    #
    # 该函数成功后，下单、查持仓等和策略帐号有关的操作都和该策略帐号绑定。
    # 没有必要每次下单、查询都调用该函数。重复调用该函数可以选择新的策略帐号。
    #
    # 如果成功，返回(strategy_id, msg)
    # 否则返回 (0, err_msg)
    sid, msg = tapi.use_strategy(9111)
    print "msg: ", msg
    print "sid: ", sid    

    # 查询Portfolio
    #
    # 返回当前的策略帐号的Universe中所有标的的净持仓，包括持仓为0的标的。

    df, msg = tapi.query_account()
    print "msg: ", msg
    df    
    
    # 查询当前策略帐号的所有持仓
    #
    # 和 query_portfolio接口不一样。如果莫个期货合约 Long, Short两个方向都有持仓，这里是返回两条记录
    # 返回的 size 不带方向，全部为 正
    df, msg = tapi.query_position()
    print "msg: ", msg
    df

    # 下单接口
    #  (task_id, msg) = place_order(code, action, price, size )
    #   action:  Buy, Short, Cover, Sell, CoverToday, CoverYesterday, SellToday, SellYesterday
    # 返回 task_id 可以用改 task_id
    task_id, msg = tapi.place_order("000025.SZ", "Buy", 57, 100)
    print "msg:", msg
    print "task_id:", task_id

    # 查询Portfolio
    #
    # 返回当前的策略帐号的Universe中所有标的的净持仓，包括持仓为0的标的。

    df, msg = tapi.query_portfolio()
    print "msg: ", msg
    df

    # 批量下单1：place_batch_order
    #
    # 返回task_id, msg。
    orders = [ 
        {"security":"600030.SH", "action" : "Buy", "price": 16, "size":1000},
        {"security":"600519.SH", "action" : "Buy", "price": 320, "size":1000},
        ]

    task_id, msg = tapi.place_batch_order(orders, "", "{}")
    print task_id
    print msg    

    # cancel_order
    # 撤单
    tapi.cancel_order(task_id)

    # 批量下单2：basket_order
    #
    # 返回task_id, msg。
	orders = [ 
		{"security":"TF1706.CFE", "ref_price": 98.240, "inc_size":10},
		{"security":"T1706.CFE",  "ref_price": 95.540, "inc_size":-17},
		]

	task_id, msg = tapi.basket_order(orders, "", "{}")
	print task_id
	print msg

    #  goal_protfolio
    #  参数：目标持仓
    #  返回：(result, msg)
    #     result:  成功或失败
    #     msg:     错误原因
    #  注意：目标持仓中必须包括所有的代码的持仓，即使不修改
    
    # 先查询当前的持仓, 
    portfolio = ts.query_portfolio()
    
    goal = pd.DataFrame(portfolio['size'])
    goal['refpx'] = 0.0
    goal['urgency'] = 10

    #  然后修改目标持仓
    code = '150131.SZ'
    goal['ref_price'][code] = 0.630
    goal['size'][code] -= 20000

    code = 'IF1712.CFE'
    goal['refpx'][code] = 4000.2
    goal['size'][code] -= 1

    # 发送请求
    result, msg = ts.goal_portfolio(goal)
    print result, msg
	
	# stop_portfolio
    # 撤单, 撤销所有portfolio订单
	tapi.stop_portfolio()

    
if __name__ == "__main__":
    test_trade_api()
