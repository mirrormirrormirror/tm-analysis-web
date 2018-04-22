!(function($) {
    var iconHtml = '<span class="icon icon-filter-arrow"></span>';
    var wrapHtml = `<div class="filter-box">` +
                        `<div class="filter-text">` +
                        `</div>` +
                    `</div>`;
    var ulHtml = `<ul class="filter-list"></ul>`;
    $.widget('ui.combobox', {
        options: {
            /**
             * @cfg {String} placeholder 为空时的提示信息
             */
            placeholder: '-- Please Select --',
            /**
             * @cfg {Boolean} editable 是否手动输入，默认为 true
             */
            editable: true,
            /**
             * @cfg {String} [dataTextField='name'] 数据源显示字段
             */
            dataTextField: "name",
            /**
             * @cfg {String} [dataValueField='value'] 数据源取值字段
             */
            dataValueField: "value",
            /**
             * @cfg {Array} [dataSource='name'] 数据源
             */
            dataSource: [],
            /**
             * @cfg {Number} [delay=500] 延迟搜索，避免过多无效搜索，单位毫秒ms，默认是500ms
             */
            delay: 500,
            /**
             * @cfg {Function} [change=null] 定义改变下拉框值事件函数，事件名称combobox:change
             */
             change: null
        },
        /**
            jQueryUI Widget生命周期方法，生成HTML，事件绑定
        */
        _create: function() {
            console.log('--- create ---');
            // 包装节点
            this.element.addClass('filter-title').attr('placeholder', this.options.placeholder);
            this.element.wrap(wrapHtml);
            this.element.after(iconHtml);
            this.element.parent().after(ulHtml);
            this.$filterText = this.element.parent();
            this.$ul = this.element.parent().siblings('ul');
            this.$icon = this.element.siblings('span');
            // 存放输入框搜索的定时器
            this.timeoutArr = [];
            // 设置是否可编辑
            this.setEditable(this.options.editable);
            // 读取 dataSource，处理数据
            this._initDataSource();
            // 绑定事件
            this._delegateEvent();
        },
        /**
            jQueryUI Widget生命周期方法
        */
        _init: function() {
            console.log('--- init ---');
        },
        _setOptions: function(options) {
            for (var key in options) {
                this._setOption(key, options[key]);
            }
            return this;
        },
        _setOption: function (key, value) {
            $.Widget.prototype._setOption.apply(this, arguments);
            if (key === 'editable') {
                this.setEditable(value);
            }
            if (key === 'disabled') {
                this.$filterText.attr('disabled', value);
                this.element.attr('disabled', value);
                this.$icon.attr('disabled', value);
            }
            return this;
        },
        setEditable: function (editable) {
            editable = !!editable;
            this.options.editable = editable;
            if (editable) {
                this.element.removeAttr('readonly');
                this._on(this.element, {
                    'keydown': '_onKeyDown'
                });
            } else {
                this.element.attr("readonly", true);
                this._off(this.element);
            }
            return this;
        },
        _destroy: function() {
            // 移除属性
            this.element.removeClass('input-combobox filter-title').removeAttr('data-value')
            .attr('readonly', false).val('');
            // 移除 dom
            this.$filterText.parent().after(this.element);
            this.$filterText.parent().remove();
        },
        _onKeyDown: function(e) {
            console.log('--- keydown ---');
            var timeout = setTimeout(function(context) {
                return function() {
                    context.timeoutArr.shift();
                    var inputVal = context.element.val();
                    if (inputVal) {
                        context.$ul.find('li').addClass('hide').not('.filter-disabled')
                        .filter(function(index, item) {
                            return item.firstChild.text.indexOf(inputVal) > -1;
                        }).removeClass('hide');
                    } else {
                        context.$ul.find('li').removeClass('hide');
                    }
                    console.log('--- delay ' + context.options.delay + 'ms search ---');
                };
            }(this), this.options.delay);
            if (this.timeoutArr.length > 0) {
                var preTimeout = this.timeoutArr.shift();
                clearTimeout(preTimeout);
            }
            this.timeoutArr.push(timeout);
        },
        _initDataSource: function() {
            // dataSource没有数据，不处理
            if (!this.options.dataSource || this.options.dataSource.length <= 0) {
                this.options.dataSource = [];
                return;
            }
            // 过滤掉 dataSource中键值对与 dataTextField、dataValueField不符合的记录
            this.options.dataSource = this.options.dataSource.filter(function(currentValue, index, arr) {
                return currentValue[this.options.dataTextField] != null 
                    && currentValue[this.options.dataValueField] != null;
            }, this);
            // 清空掉 item选项
            this.$ul.empty();
            if (this.options.dataSource && this.options.dataSource.length) {
                $.each(this.options.dataSource, function (i, item) {
                    this._appendToUl(item);
                }.bind(this));
            }
        },
        _appendToUl: function(item) {
            // 处理dataTextField的值为非字符串的问题
            item[this.options.dataTextField] += "";
            // 组建 item
            var liHtml = 
                `<li data-value="#{value}" class="#{class}"><a title="#{title}">#{text}</a></li>`;
            liHtml = $.fn.format(liHtml, {
                value: item[this.options.dataValueField],
                text: item[this.options.dataTextField],
                title: item[this.options.dataTextField],
                class: ((item.selected ? 'filter-selected' : '') 
                    + ' ' + (item.disabled ? 'filter-disabled' : '')).trim()
            });
            this.$ul.append(liHtml);
            if (item.selected) {
                // 设置 item选中
                this._select(item);
            }
        },
        _delegateEvent: function() {
            // 展示/隐藏 组件内容
            this.$filterText.on('click.combobox', 'input, span', function() {
                if (!this.options.disabled) {
                    this.$ul.slideToggle(100);
                    this.$ul.toggleClass('filter-open');
                    this.$icon.toggleClass('filter-show');
                }
            }.bind(this));
            $(this.document).on('mousedown.combobox', function(e) {
                var target = e.target ? e.target : e.srcElement;
                // 过滤某些元素，点击后不触发
                if (target.parentNode !== this.$filterText.get(0) && target !== this.$filterText.get(0)
                    && target.parentNode.parentNode !== this.$ul.get(0)) {
                    this.$ul.slideUp(100);
                    this.$ul.removeClass('filter-open');
                    this.$icon.removeClass('filter-show');
                }
            }.bind(this));
            // 选择某一项内容，回显
            $(this.$ul).on('click.combobox', 'li:not(.filter-disabled)', function(e) {
                var currentTarget = e.currentTarget;
                // 设置其选中样式
                this._select({
                    value: $(currentTarget).attr('data-value'),
                    name: currentTarget.firstChild.text
                });
                // 隐藏选项组
                this.$ul.slideToggle(100);
                this.$ul.toggleClass('filter-open');
                this.$icon.toggleClass('filter-show');
                this.$ul.find('li').removeClass('hide');
            }.bind(this));
        },
        /**
         * @method value 取值或者赋值
         * @param  {String} [value] 设置值选中,为空则取控件值
         * @return {String} 控件值,赋值操作则没有返回值
         */
        value: function(value) {
            if (arguments.length === 0) { // 取值操作
                console.log('--- get value ---');
                return this.$ul.find('li[class="filter-selected"]').attr('data-value');
            }
            // 赋值操作
            console.log('--- set value ---');
            var selectedItem = null;
            for(var i = 0, len = this.options.dataSource.length; i < len; i++) {
                var item = this.options.dataSource[i], isSelected = item.selected;
                if (item[this.options.dataValueField] === value && !item.disabled) {
                    selectedItem = item;
                    break;
                }
            }
            this._select(selectedItem);
        },
        _select: function(item) {
            if (item) {
                var value = item[this.options.dataValueField],
                    text = item[this.options.dataTextField];
                this.element.val(text);
                // 判断选择的节点是否和上一个选择的节点相同
                if (this.element.attr('data-value') !== value) {
                    this.$ul.find('li').removeClass('filter-selected').filter(function(index, element) {
                        return $(element).attr('data-value') === value;
                    }.bind(this)).addClass('filter-selected');
                    this.element.attr('data-value', value);
                    this._trigger('change', null, {
                        value: value,
                        text: text
                    });
                }
            } else {
                this.$ul.find('li').removeClass('filter-selected');
                this.element.val('');
                this.element.removeAttr('data-value');
                this._trigger('change');
            }
        },
        /**
         * @method clear 清空选择内容
         */
        clear: function() {
            this._select(null);
        },
        /**
         * @method getSelectedItem 获取被选中的项键值对
         * @return 键值对
         */
        getSelectedItem: function() {
            console.log('--- getSelectedItem ---');
            return {
                value: this.element.attr('data-value'),
                text: this.element.val()
            }
        },
        /**
         * @method append 向 dataSource里追加数据，显示在页面上
         * @param  {Array} [items] 追加的内容
         * @return this
         */
        append: function(items) {
            // 传入参数不是数组，直接返回控件对象 this
            if (!(items instanceof Array)) {
                return this;
            }
            // 过滤掉键值对与 options参数不一致的内容
            items = items.filter(function(item, index) {
                return item.hasOwnProperty(this.options.dataValueField) 
                    && item.hasOwnProperty(this.options.dataTextField);
            }.bind(this));
            if (items.length === 0) {
                return this;
            }
            // 将追加的数据放入到 options里，并追加到 ul元素里面
            Array.prototype.push.apply(this.options.dataSource, items);
            $.each(items, function(index, item) {
                this._appendToUl(item);
            }.bind(this));
            return this;
        },
        /**
         * @method remove 从 dataSource中移除某些项
         * @param  {Array} [items] 移除的内容
         * @return this
         */
        remove: function(items) {
            // 传入参数不是数组，直接返回控件对象 this
            if (!(items instanceof Array)) {
                return this;
            }
            // 过滤掉键值对与 options参数不一致的内容
            items = items.filter(function(item, index) {
                return item.hasOwnProperty(this.options.dataValueField) 
                    && item.hasOwnProperty(this.options.dataTextField);
            }.bind(this));
            if (items.length === 0) {
                return this;
            }
            // 从 options里移除，并从 ul元素里面移除
            $.each(items, function(index, item) {
                var $target = this.$ul.find('li[data-value=' + item[this.options.dataValueField] + ']')
                .find('a[title='+ item[this.options.dataTextField] +']').end().addClass('hide');
                var pos = $target.prevAll().length;
                this.options.dataSource.splice(pos, 1);
                // 若移除的元素被选中，则需要清空选中
                if ($target.hasClass('filter-selected')) {
                    this._select(null);
                }
            }.bind(this));
            return this;
        }
    });
    /**
        在 jQuery的原型链上新增一个格式化函数
    */
    jQuery.fn.format = function(str) {
        var args = Array.prototype.slice.call(arguments, 1);
        var reg = /\#{([^{}]+)}/gm; 
        return str.replace(reg, function(match, name, index, str) {
            // 判断括号匹配的内容是否是数字
            var content = Number(name);
            if (content >= 0) {
                return args[content];
            }
            // 不是数字的话，应该就是对象
            var object = args[0];
            if (object && object !== void(0)) {
                return object[name];
            }
            // 未匹配到，返回空串
            return '';
        });
    }
})(jQuery)