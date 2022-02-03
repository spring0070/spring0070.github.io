---
layout: post
title: Jekyll on Github
tags: [程式開發]
categories:
  - Article
excerpt_separator:  <!--more-->
---

## Github + Ruby + Jekyll + Mac 環境

### 安裝 Ruby 3.0
{% highlight js %}
$brew install ruby
{% endhighlight %}

### 改Mac ruby 讀取位置
{% highlight js %}
$vi .zprofile
export PATH=/opt/homebrew/Cellar/ruby/3.0.3/bin:/usr/local/bin:/opt/homebrew/bin:$PATH
{% endhighlight %}

### 確認Mac 可以讀到正確的Ruby版本 
{% highlight js %}
$ruby -v
ruby 3.0.3p157 (2021-11-24 revision 3fb7d2cadc) [arm64-darwin21]
{% endhighlight %}

### 下載想要的 Jekyll Theme
[hydeout theme](http://jekyllthemes.org/themes/hydeout/).

### 更新缺少Ruby套件 rdoc 
{% highlight js %}
$sudo gem install rdoc
{% endhighlight %}

### 更新缺少Ruby套件 webrick 
{% highlight js %}
$sudo gem install webrick
{% endhighlight %}

### 安裝主要Jekyll
{% highlight js %}
$sudo gem install jekyll
$sudo gem install jekyll bundler
{% endhighlight %}

### 在專案目錄夾下 
{% highlight js %}
$sudo bundle install 
{% endhighlight %}

### 在專案目錄夾下更新缺少套件
{% highlight js %}
$sudo bundle add webrick
{% endhighlight %}

### 在專案目錄夾下把網站帶起來
{% highlight js %}
$sudo bundle exec jekyll serve --trace
{% endhighlight %}

### 本機測試
[http://127.0.0.1:4000/](http://127.0.0.1:4000/).

### 成功後就可以上傳到Github了
{% highlight js %}
建議使用sourcetree 綁定ssh 來git push
{% endhighlight %}





