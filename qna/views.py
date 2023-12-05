from django.shortcuts import render, redirect
from django.http import HttpResponse
from qna.models import PublicChatRoom, Answer
import json
from django.db.models import Count


# Create your views here.
def pika_view(request):

    if not request.user.is_authenticated:
        return redirect('login')

    context = {}

    question_answers = [] # ['{question' : {answers}}]

    # questions = PublicChatRoom.objects.all()
    questions = PublicChatRoom.objects.all().order_by('-timestamp')
    # questions = PublicChatRoom.objects.all().exclude(answers__user = request.user)
    questions = questions.order_by('-timestamp')
    

    for question in questions:
        # question_answers.append([question, question.answers.all()])
        # print('question - ', question)
        answers_with_descendants = []

        answers = question.answers.filter(parent=None).annotate(report_count=Count('ans_reports')).exclude(report_count__gt=10)
        answers = answers.annotate(num_likes=Count('likes'))
        answers = answers.order_by('-num_likes')[:1]

        top2_ans = []
        for answer in answers:
            # print('The parent answer - ', answer)
            
            answers_and_replies = [answer] + list(answer.get_descendants())
            answers_with_descendants.extend(answers_and_replies) 
            top2_ans.append(answer.pk)
        
        # assuming that above instead of sending the first 2 answers we have send the top 2 answers , now we want to send the rest of the answers excluding the above 2

        other_answers_with_descendants = []

        answers = question.answers.filter(parent=None).exclude(id__in=top2_ans)
        answers = answers.order_by('-timestamp')
        for answer in answers:
            # print('This is what the pending answers are - ', answer)
            print('The answer - ',answer,' The reports - ',answer.ans_reports.all().count())
            if answer.ans_reports.all().count() < 5:
                other_answers_and_replies = [answer] + list(answer.get_descendants())
                other_answers_with_descendants.extend(other_answers_and_replies) 
        


        
        question_answers.append([question,answers_with_descendants, other_answers_with_descendants])
            
        
    # print(question_answers)

        # print(question)
    #     answers = Answer.objects.filter(question = question , parent=None)
    #     replies = Answer.objects.filter(question = question).exclude(parent=None)
    #     print('The Answers of the question - ', answers)
    #     print('The replies on the answers - ', replies)
    
    # for answer in question_answers:
    #     for sub_ans in answer[1]:
    #         print('This is the what - ', sub_ans)

    # print(question_answers)

    # context['questions'] = questions
    context['question_top2_answers'] = question_answers


    # if request.method == 'POST':
    #     question_id = request.POST.get('question-id')
    #     print('The question id is -', question_id)
    #     content = request.POST.get('id_chat_message_input')
    #     user = request.user

    #     try:
    #         question = PublicChatRoom.objects.get(pk=question_id)

    #         parent_id = request.POST.get('answer-id')
    #         print('The parent id is - ', parent_id)
    #         if parent_id:
    #             parent = Answer.objects.get(pk=parent_id)
    #             answer = Answer(question = question, user = user, content=content, parent=parent)
    #             answer.save()
    #         else:
    #             answer = Answer(question = question, user = user, content=content)
    #             answer.save()
    #     except PublicChatRoom.DoesNotExist:
    #         print('Error - question/answer doesn not exist!')

    #     return redirect('qna:pika')



    return render(request, "qna/questions.html", context)

def create_post_view(request):

    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':

        user = request.user
        question = request.POST.get('question')

        roomv = PublicChatRoom(question = question, owner = user)
        roomv.save()
        
        return redirect('qna:pika')

    return render(request, 'qna\create_question.html')

def minichat_view(request, *args, **kwargs):
    return render(request, "qna\qnaroom.html")


def addAnswer_view(request, *args, **kwargs):

    print('The addAnswer view is called')
    user = request.user

    if not request.user.is_authenticated:
        return redirect("login")

    if request.POST:

        if request.POST.get('action') == 'report':

            print('ans report request arrived')
            id = request.POST.get('node-id')
            reporter = request.user

            try:
                answer = Answer.objects.get(pk=id)
                if reporter in answer.ans_reports.all():
                    # You have already reported this person
                    response_data = {
                'status' : 'success',
                'response' : 'Already Reported',
            }
                else:
                    # The person is reported 
                    answer.add_flag(reporter)
                    response_data = {
                'status' : 'success',
                'response' : 'reported',
            }
                
                print('This answer/reply is getting reported - ', answer)

            except Exception as e :
                print('error fetching the answer')
                response_data = {
                'status' : 'error',
                'message': str(e),
            }


        if request.POST.get('action') == 'delete':

            print('post delete request arrived')

            id = request.POST.get('node-id')
            print('The delete id is -', id)
            try:
                answer = Answer.objects.get(pk=id)
                print('This answer is getting deleted - ', answer)

                if answer.user == request.user:
                    answer.delete()

                response_data = {
                'status' : 'delete done',
                'response' : 'card deleted'
            }
            except Exception as e:
                print('error fetching the answer')
                response_data = {
                'status' : 'error',
                'message': str(e),
            }


           
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        
        if request.POST.get('action') == 'delete_my_question':

            print('post delete question request arrived')

            id = request.POST.get('node-id')
            print('The delete question id is -', id)
            try:
                question = PublicChatRoom.objects.get(pk=id)
                print('This question is getting deleted - ', question)

                if question.owner == request.user:
                    question.delete()

                response_data = {
                'status' : 'delete done',
                'response' : 'card deleted'
            }
            except Exception as e:
                print('error fetching the answer')
                response_data = {
                'status' : 'error',
                'message': str(e),
            }


           
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        

        if request.POST.get('action') == 'like':

            print('post like request arrived')
            id = request.POST.get('node-id')

            try:
                answer = Answer.objects.get(pk=id)
                answer.add_like(request.user)
                count = answer.likes.all().count()
                response_data = {
                'status' : 'like added',
                'response' : 'liked',
                'count' : count,
            }
            except Exception as e:
                print('error fetching the answer')
                response_data = {
                'status' : 'error',
                'message': str(e),
            }
            
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        
        if request.POST.get('action') == 'unlike':

            print('post unlike request arrived')
            id = request.POST.get('node-id')

            try:
                answer = Answer.objects.get(pk=id)
                answer.remove_like(request.user)
                
                response_data = {
                'status' : 'unlike added',
                'response' : 'unliked',
                
            }
            except Exception as e:
                print('error fetching the answer')
                response_data = {
                'status' : 'error',
                'message': str(e),
            }
            
            return HttpResponse(json.dumps(response_data), content_type="application/json")


        try:
            
            question_id = request.POST.get('question-id')
            print('The question id is -', question_id)
            content = request.POST.get('id_chat_message_input')
            user = request.user

            try:
                question = PublicChatRoom.objects.get(pk=question_id)

                parent_id = request.POST.get('answer-id')
                print('The parent id is - ', parent_id)
                if parent_id:
                    parent = Answer.objects.get(pk=parent_id)
                    answer = Answer(question = question, user = user, content=content, parent=parent)
                    answer.save()
                    response_data = {
                        'status' : 'Replied',
                        'message': 'Your reply has been added.',
                        'name' : user.name,
                        'content' : content,
                        'domain' : user.university_name,
                        'nodeId' : answer.id,
                        
                    }
                else:
                    print('this is the before ans - ')
                    answer = Answer(question = question, user = user, content=content)
                    answer.save()
                    print('this is the ans - ', answer)
                    response_data = {
                        'status' : 'Answered',
                        'message': 'Your answer has been added.',
                        'name' : user.name,
                        'content' : content,
                        'domain' : user.university_name,
                        'nodeId' : answer.id,
                        
                    }

            except PublicChatRoom.DoesNotExist:
                print('Error - question/answer doesn not exist!')

        except Exception as e:
            print('The addAnswer/reply exception is - ', str(e))
            response_data = {
                'status' : 'error',
                'message': str(e),
            }

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def show_ques_view(request,*args, **kwargs):

    ans_id = kwargs.get('ans_id')
    context = {}

    try:
        answer = Answer.objects.get(pk=ans_id)
        ques_id = answer.question.id
        question = PublicChatRoom.objects.get(pk=ques_id)

        # now gotta check whether this answer is a answer or a reply
        if answer.parent:
            context['ans_id'] = int(ans_id)
            context['highlight_reply'] = int(ans_id)

            try:
                child_node = Answer.objects.get(id=ans_id)
                ancestors = child_node.get_ancestors(ascending=True)  # ascending=True returns ancestors from root to parent

                # ------------------------------------------------------------------------

                # nodes_to_expand = child_node.get_ancestors(include_self=True).values_list('id', flat=True)

                # # Pass nodes_to_expand to your template
                # context = {'nodes_to_expand': nodes_to_expand}

                # The first element in the ancestors list will be the root ancestor
                root_ancestor = child_node.get_root()
                parent_id = child_node.parent.id
                print('This is the fuckin parent id - ', parent_id)
                context['parent_id'] = parent_id

                answer = root_ancestor

                print('This is his parent root answer - ', root_ancestor)

                question_answers = [] # ['{question' : {answers}}]

                answers_with_descendants = []

                # answers = question.answers.filter(parent=None)
                # answers = answers.annotate(num_likes=Count('likes'))
                # answers = answers.order_by('-num_likes')[:1]

                top2_ans = []
                # for answer in answers:
                    # print('The parent answer - ', answer)
                answers_and_replies = [answer] + list(answer.get_descendants())
                # answers_and_replies = [answer] + list(answer.get_descendants().order_by('-timestamp'))
                answers_with_descendants.extend(answers_and_replies) 
                top2_ans.append(answer.pk)
                
                # assuming that above instead of sending the first 2 answers we have send the top 2 answers , now we want to send the rest of the answers excluding the above 2

                other_answers_with_descendants = []

                answers = question.answers.filter(parent=None).exclude(id__in=top2_ans)
                answers = answers.order_by('-timestamp')
                for answer in answers:
                    # print('This is what the pending answers are - ', answer)
                    print('The answer - ',answer,' The reports - ',answer.ans_reports.all().count())
                    if answer.ans_reports.all().count() < 5:
                        other_answers_and_replies = [answer] + list(answer.get_descendants())
                        other_answers_with_descendants.extend(other_answers_and_replies) 
                


                
                question_answers.append([question,answers_with_descendants, other_answers_with_descendants])

                context['question'] = question_answers
                print('The question answers are -', question_answers)
                print('This is the fuckin id i have -',ans_id, type(ans_id))

            except Answer.DoesNotExist:
                return None
            
        else:
            context['ans_id'] = ans_id
            context['highlight_answer'] = ans_id
            
            # context['question'] = question

            question_answers = [] # ['{question' : {answers}}]

            answers_with_descendants = []

            # answers = question.answers.filter(parent=None)
            # answers = answers.annotate(num_likes=Count('likes'))
            # answers = answers.order_by('-num_likes')[:1]

            top2_ans = []
            # for answer in answers:
                # print('The parent answer - ', answer)
            answers_and_replies = [answer] + list(answer.get_descendants())
            answers_with_descendants.extend(answers_and_replies) 
            top2_ans.append(answer.pk)
            
            # assuming that above instead of sending the first 2 answers we have send the top 2 answers , now we want to send the rest of the answers excluding the above 2

            other_answers_with_descendants = []

            answers = question.answers.filter(parent=None).exclude(id__in=top2_ans)
            answers = answers.order_by('-timestamp')
            for answer in answers:
                # print('This is what the pending answers are - ', answer)
                print('The answer - ',answer,' The reports - ',answer.ans_reports.all().count())
                if answer.ans_reports.all().count() < 1:
                    other_answers_and_replies = [answer] + list(answer.get_descendants())
                    other_answers_with_descendants.extend(other_answers_and_replies) 
            


            
            question_answers.append([question,answers_with_descendants, other_answers_with_descendants])

            context['question'] = question_answers
            print('The question answers are -', question_answers)

            
    except Answer.DoesNotExist:
        return HttpResponse('The question/answer you are looking for does not exist!')


    return render(request, "qna/quest.html", context)