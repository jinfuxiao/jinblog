from django.db import models
from django.utils.functional import cached_property


class Article(models.Model):
    title = models.CharField(max_length=128)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    # 方法属性化，并存入缓存，因为不会经常更新
    @cached_property
    def tags(self):
        article_tags = ArticleTags.objects.filter(aid=self.id).only('tid')
        tid_list = [at.tid for at in article_tags]
        return Tag.objects.filter(id__in=tid_list)

    @classmethod
    def update_article_tags(self, tag_names):
        # 该文章已有的tags
        old_tag_names = set(tag.name for tag in self.tags)
        # 需要新增的tags
        new_tag_names = set(tag_names) - old_tag_names
        # 需要删除的tags
        need_delete = old_tag_names - set(tag_names)

        # 创建新的关系
        Tag.create_new_tags(new_tag_names, self.id)

        # 删除旧关系
        need_delete_tids = [t.id for t in Tag.objects.filter(name__in=need_delete).only('id')]
        articletags = ArticleTags.objects.filter(tid__in=need_delete_tids)
        for atag in articletags:
            atag.delete()


        # 取出需要删除的关系的 tid
        # need_delete = []
        # for tag in self.tags:
        #     if tag.name not in tag_names:
        #         need_delete.append(tag.id)
        #     else:
        #         tag_names.remove(tag.name)  # 需要保留的已有的tags, 剔除掉，剩下的就是需要新建的
        # 删除旧的关系
        # articletags = ArticleTags.objects.filter(tid__in=need_delete)
        # for atag in articletags:
        #     atag.delete()

        # 创建新的 Tag 和 关系
        # Tag.create_new_tags(tag_names, self.id)


class Comment(models.Model):
    aid = models.IntegerField()
    name = models.CharField(max_length=128, blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True, blank=False, null=False)

    # 创建文章的时候创建tags，编辑文章的时候要做的是更新tags--两个函数
    # 创建 Tags
    # 1，需要创建的tag_names->创建tags本身, 文章的aid->建立关系,
    # 1.1，创建tags本身，首先判断数据库是不是有这个tag，有的话不需要重复创建，没有的话创建
    # 1.2，把所有的tag_names和aid建立起关系
    # 定义成类方法，直接通过类调用函数就行

    @classmethod
    def create_new_tags(cls, tag_names, aid):
        # 取出数据库已存在的 tags
        exist_tags = cls.objects.filter(name__in=tag_names).only('name')
        # 取出这些 tags 的 name
        exists = [t.name for t in exist_tags]
        # 去除已存在的 tags --差集
        new_tags = set(tag_names) - set(exists)

        # 我的思路
        # exists = cls.objects.all().only('name')
        # new_tags = set(tag_names) - set(exists)

        # 生成待创建的 Tag 对象列表
        new_tags = [cls(name=n) for n in new_tags]
        # 批量创建，bulk_create(列表)，返回的是创建好的对象列表
        cls.objects.bulk_create(new_tags)

        # 建立与 Article 的关系，是在关系表中建立，update_or_create需要创建在关系表中
        tags = cls.objects.filter(name__in=tag_names)
        for t in tags:
            ArticleTags.objects.update_or_create(aid=aid, tid=t.id)
        return tags

    # 获取某一标签对应的文章，方法属性化
    @property
    def articles(self):
        aid_list = [at.aid for at in ArticleTags.objects.filter(tid=self.id).only('aid')]
        return Article.objects.filter(id__in=aid_list)


class ArticleTags(models.Model):
    aid = models.IntegerField()
    tid = models.IntegerField()

# 首页暂时先不考虑-base.html增加右边栏，文章详情页有 标签 显示
# 文章编辑和发表有添加标签的功能，这样在发表文章的时候aid就和tid关联起来
# url，增加一个点击标签跳转到相应文章的路径，查看一篇文章的相应标签是
    # path('post/tag/', post_views.get_tag_articles),
# view，增加一个函数，处理对应的url，获取到相关文章


