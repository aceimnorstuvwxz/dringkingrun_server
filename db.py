import mysql.connector
'''
(C)2015 chenbingfeng@TurnroGame.com
'''

class Dmdb:
    """ DB operation of drinking running server"""
    
    #class variables
    USER = "root"
    PASSWORD = "123456"
    DATABASE = "db_drinking_man"
    ADD_DRINK = '''
    INSERT INTO `db_drinking_man`.`drinks`
(
`id_string`,
`name`,
`image`,
`score`,
`gold`,
`config`,
`cost_rmb`,
`pass_md5`)
VALUES
(%(id_string)s,%(name)s,%(image)s,%(score)s,%(gold)s,%(config)s,%(cost_rmb)s,%(pass_md5)s)
    '''
    SELECT_BY_ID = '''
    SELECT id, id_string, name, image, score, gold, config, cost_rmb, pass_md5 
FROM `db_drinking_man`.`drinks` WHERE id=%s
'''
    SELECT_TOP_3 = '''
    SELECT id, id_string, name, image, score, gold, config, cost_rmb, pass_md5 
FROM `db_drinking_man`.`drinks` ORDER BY score DESC LIMIT 0,3
'''
    COUNT_SCORE_RANK = '''
    SELECT count(*) as co
FROM `db_drinking_man`.`drinks` 
WHERE score>%s
'''
    SELECT_A_B = '''
    SELECT id, id_string, name, image, score, gold, config, cost_rmb, pass_md5 
FROM `db_drinking_man`.`drinks` ORDER BY score DESC LIMIT %s,%s
    '''
    
    UPDATE = '''
    UPDATE `db_drinking_man`.`drinks` 
SET id_string = %s,
name = %s,
image = %s,
score = %s,
gold = %s,
config = %s,
cost_rmb = %s,
pass_md5 = %s
WHERE id = %s
'''
    IS_STRING_EXIST = '''
    SELECT id_string, name FROM db_drinking_man.drinks WHERE id_string = %s
'''
    def __init__(self):
        #connect to DB
        print("connect to DB")
        self.context = mysql.connector.connect(user=self.USER, password=self.PASSWORD, database=self.DATABASE)

    def __del__(self):
        print("disconnect to DB")
        self.context.close()
        
    def insert(self, dict):
        ''' insert may raise exception because of duplicate id_string '''
        try:
            cursor = self.context.cursor()
            cursor.execute(self.ADD_DRINK, dict)
            self.context.commit()
            cursor.close()
            return True
        except mysql.connector.errors.IntegrityError:
            return False
        
    
    def update(self, dict):
        cursor = self.context.cursor()
        cursor.execute(self.UPDATE, (
                       dict["id_string"],
                       dict["name"],
                       dict["image"],
                       dict["score"],
                       dict["gold"],
                       dict["config"],
                       dict["cost_rmb"],
                       dict["pass_md5"],
                       dict["id"]
                       ))
        cursor.close()
        
    def turple2dict(self, turp):
        if (turp == None):
            return None
        else:
            res = {}
            res["id"] = turp[0]
            res["id_string"] = turp[1]
            res["name"] = turp[2]
            res["image"] = turp[3]
            res["score"] = turp[4]
            res["gold"] = turp[5]
            res["config"] = turp[6]
            res["cost_rmb"] = turp[7]
            res["pass_md5"] = turp[8]
            return res    
        
    def getById(self, id):
        ''' get data by Id, if not exist, return None '''
        cursor = self.context.cursor()
        cursor.execute(self.SELECT_BY_ID, (id,))
        res = None
        for turp in cursor:
            res =  self.turple2dict(turp)
            break
        cursor.close()
        return res
    
    def isIdStringExist(self, id_string):
        ''' check if id_string exist '''
        cursor = self.context.cursor()
        cursor.execute(self.IS_STRING_EXIST, (id_string,)) 
        res = False
        for tp in cursor:
            res = True
            break
        cursor.close()
        return res
    
    def getTopAB(self, a, b):
        ''' get limit a, b '''
        cursor = self.context.cursor()
        cursor.execute(self.SELECT_A_B, (a, b))
        res = []
        for turp in cursor:
            res.append(self.turple2dict(turp))
        cursor.close()
        return res
    
    def getTopScore3(self):
        ''' get top 3 record '''
        return self.getTopAB(0, 3)
    
    def countScoreRank(self, score):
        ''' count (record > score) '''
        cursor = self.context.cursor()
        cursor.execute(self.COUNT_SCORE_RANK, (score,))
        res = 0
        for turp in cursor:
            res = turp[0]
            break
        cursor.close()
        return res
    
    def getNear6ByScore(self, score):
        rank = self.countScoreRank(score)
        if rank < 3:
            rank = 3
        return self.getTopAB(rank-3, rank+3)

if __name__ == "__main__":
    ''' TEST CODE '''
    db = Dmdb()
    drink = {
    "id_string":"my_id_string",
    "name":"my_name",
    "image":"image",
    "score":3243,
    "gold":23432,
    "config":'{"sdfsdgijoi324325":23432}',
    "cost_rmb":"2343",
    "pass_md5":"sdfsdfs234"
    }
    '''
    for i in xrange(100):
        drink["score"] = i
        drink["id_string"] = "id_string_%s" % (i,)
        #db.insert(drink)
    '''
    #db.insert(drink)
    #db.insert(drink)
    #print db.getById(1)
#     print db.isIdStringExist("my_id_string")
#     a = db.getById(1)
#     print a
#     a["name"] = "abc"
#     print a
#     db.update(a)
#     print db.getById(1)
    del db