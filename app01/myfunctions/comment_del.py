from app01 import models


class CommentDel(object):
    count = 1

    @classmethod
    def cascade_del(cls, comment_id):
        comment_obj = models.Comment.objects.filter(id=comment_id).first()
        comment_obj.is_del = True
        comment_obj.save()
        child_obj_query_set = models.Comment.objects.filter(parent_id=comment_id)
        if len(child_obj_query_set) == 0:
            return 1
        cls.count += len(child_obj_query_set)
        for i in child_obj_query_set:
            CommentDel.cascade_del(i.id)
        return cls.count


class CommentRecover(object):

    def __call__(self, article_id):
        """
        Input a article_id recover all comments included for this article and modify the comment_num field in Article Table
        for the record with this id as primary key
        :param article_id:
        :return:
        """
        effect_record_num = models.Comment.objects.filter(article_id=article_id).update(is_del=False)
        models.Article.objects.filter(id=article_id).update(comment_num=effect_record_num)
