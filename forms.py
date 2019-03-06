from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, RadioField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Email


class LoginForm(FlaskForm):
    username = StringField(u"用户", validators=[DataRequired()])
    password = PasswordField(u"密码", validators=[DataRequired(), EqualTo('confirm', message=u'密码不正确，请重新输入')])
    submit = SubmitField(u'登录')


class RegisterForm(FlaskForm):
    # 约束条件在validator里加
    username = StringField(validators=[DataRequired(), Length(1, 40)])
    password = PasswordField(validators=[DataRequired(), Length(1, 20), EqualTo('password2', message='D_input')])
    password2 = PasswordField(validators=[DataRequired(), Length(1, 20)])
    email = StringField(validators=[DataRequired(), Length(1, 20), Email()])
    submit = SubmitField()


class SearchForm(FlaskForm):
    trade = RadioField(u'交易类型', choices=[
        ('buy', u'专利购买信息'),
        ('sell', u'专利售卖信息')
    ], validators=[DataRequired()])
    query = StringField(u'查询', validators=[DataRequired()])
    ptype = SelectField(u"专利类型", choices=[
        ('', ''),
        (u'发明', u'发明专利'),
        (u'实用', u'实用创新型专利'),
        (u'外观', u'外观专利'),
        (u'类型不限', u'类型不限')
    ])
    cond = SelectField(u"专利状态", choices=[
        ('', ''),
        (u'未缴费', u'授权未缴费'),
        (u'下证', u'缴费已下证'),
        (u'不限', u'状态不限')
    ])
    # time = StringField('日期(年-月-日)')
    submit = SubmitField(u'搜索')


class SqlForm(FlaskForm):
    pid = StringField(u'专利号')
    trade = RadioField(u'交易类型', choices=[
        ('buy', u'专利购买信息'),
        ('sell', u'专利售卖信息')
    ], validators=[DataRequired()])
    keyword = StringField(u'关键字')
    ptype = SelectField(u"专利类型", choices=[
        ('', ''),
        (u'发明', u'发明专利'),
        (u'实用', u'实用创新型专利'),
        (u'外观', u'外观专利'),
        (u'类型不限', u'类型不限')
    ])
    cond = SelectField(u"专利状态", choices=[
        ('', ''),
        (u'未缴费', u'授权未缴费'),
        (u'下证', u'缴费已下证'),
        (u'不限', u'状态不限')
    ])
    time = StringField('日期(年-月-日)')
    contact = StringField('联系方式')
    submit = SubmitField(u'搜索')
