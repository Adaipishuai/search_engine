from django import forms

class SimpleSearchForm(forms.Form):
    query = forms.CharField(
        label='',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入关键字...'
        })
    )

class AdvancedSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        max_length=100,
        label="关键词",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "请输入关键词"})
    )
    authors = forms.CharField(
        required=False,
        max_length=100,
        label="作者",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "作者"})
    )
    tags = forms.CharField(
        required=False,
        max_length=100,
        label="标签",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "标签"})
    )
    click_min = forms.IntegerField(
        required=False,
        label="点击量最小值",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    click_max = forms.IntegerField(
        required=False,
        label="点击量最大值",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    char_min = forms.IntegerField(
        required=False,
        label="字数最小值",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    char_max = forms.IntegerField(
        required=False,
        label="字数最大值",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )