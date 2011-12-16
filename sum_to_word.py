# -*- coding: utf-8 -*-

class _RusNumber(object):

    hunds = [u"", u"сто ", u"двести ", u"триста ", u"четыреста ",
        u"пятьсот ", u"шестьсот ", u"семьсот ", u"восемьсот ", u"девятьсот "]

    tens =[u"", u"десять ", u"двадцать ", u"тридцать ", u"сорок ", u"пятьдесят ",
            u"шестьдесят ", u"семьдесят ", u"восемьдесят ", u"девяносто "]


    def Str(self, val, male, one, two, five):

        frac20 =[u"", u"один ", u"два ", u"три ", u"четыре ", u"пять ", u"шесть ",
                u"семь ", u"восемь ", u"девять ", u"десять ", u"одиннадцать ",
                u"двенадцать ", u"тринадцать ", u"четырнадцать ", u"пятнадцать ",
                u"шестнадцать ", u"семнадцать ", u"восемнадцать ", u"девятнадцать "]


        num = val % 1000;
        if 0 == num: return u""
        if num < 0: return u""

        if not male:
            frac20[1] = u"одна ";
            frac20[2] = u"две ";


        # StringBuilder r = new StringBuilder(hunds[num / 100]);
        r = [self.hunds[num/100]]
        if num % 100 < 20:
            r.append(frac20[num % 100]);
        else:
            r.append(self.tens[num % 100 / 10]);
            r.append(frac20[num % 10]);


        r.append(self.Case(num, one, two, five));

        if (len(r) != 0): r.append(u" ")
        return ''.join(r)



    def Case(self, val, one, two, five):
        t=val % 10 if (val % 100 > 20) else val % 20
        if t==1:
            return one;
        elif t==2 or t==3 or t==4:
            return two
        else:
            return five

class CurrencyInfo(object):
    male = False
    seniorOne=seniorTwo=seniorFive=''
    juniorOne=juniorTwo=juniorFive=''


class RusCurrency(object):
    currencies = {}
    RusCurrency ={
        u"RUR":(True, u"рубль ", u"рубля ", u"рублей ", u" копейка", u" копейки", u" копеек"),
        u"EUR": (True, u"евро", u"евро", u"евро", u"евроцент", u"евроцента", u"евроцентов"),
        u"USD": (True, u"доллар", u"доллара", u"долларов", u"цент", u"цента", u"центов")}

    def __init__(self):
        for k,v in self.RusCurrency.items():
            info = CurrencyInfo()
            info.male = v[0];
            info.seniorOne = v[1]; info.seniorTwo = v[2]; info.seniorFive = v[3];
            info.juniorOne = v[4]; info.juniorTwo = v[5]; info.juniorFive = v[6];
            self.currencies.update({k:info});


    def Str(self, val, currency):
        if not currency in self.currencies:
            return u'';


        info = self.currencies[currency];
        return self._Str(val, info.male,
                info.seniorOne, info.seniorTwo, info.seniorFive,
                info.juniorOne, info.juniorTwo, info.juniorFive);



    def _Str(self, val, male, seniorOne, seniorTwo, seniorFive,juniorOne, juniorTwo, juniorFive):
        RusNumber = _RusNumber()
        minus = False;
        if(val < 0):
            val = - val; minus = True

        n = int(val);
        remainder =  int(( val - n + 0.005 ) * 100);

        r = []

        if(0 == n): r.append(u"0 ");
        if(n % 1000 != 0):
            r.append(RusNumber.Str(n, male, seniorOne, seniorTwo, seniorFive));
        else:
            r.append(seniorFive);

        n /= 1000;

        r.insert(0, RusNumber.Str(n, False, u"тысяча", u"тысячи", u"тысяч"));
        n /= 1000;

        r.insert(0, RusNumber.Str(n, True, u"миллион", u"миллиона", u"миллионов"));
        n /= 1000;

        r.insert(0, RusNumber.Str(n, True, u"миллиард", u"миллиарда", u"миллиардов"));
        n /= 1000;

        r.insert(0, RusNumber.Str(n, True, u"триллион", u"триллиона", u"триллионов"));
        n /= 1000;

        r.insert(0, RusNumber.Str(n, True, u"триллиард", u"триллиарда", u"триллиардов"));
        if(minus): r.insert(0, u"минус ");

        r.append(str(remainder));
        r.append(RusNumber.Case(remainder, juniorOne, juniorTwo, juniorFive));

        #Делаем первую букву заглавной
        i = 0
        for s in r:
            if len(s)>0:
                r[i] = s[0].upper()+s[1:]
                break
            i+=1
        
        return u''.join(r)

#print RusCurrency().Str(34000, 'RUR').encode('utf-8')
