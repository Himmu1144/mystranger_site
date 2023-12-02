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

        answers = question.answers.filter(parent=None)
        answers = answers.annotate(num_likes=Count('likes'))
        answers = answers.order_by('-num_likes')[:2]

        top2_ans = []
        for answer in answers:
            # print('The parent answer - ', answer)
            answers_and_replies = [answer] + list(answer.get_descendants())
            answers_with_descendants.extend(answers_and_replies) 
            top2_ans.append(answer.pk)
        
        # assuming that above instead of sending the first 2 answers we have send the top 2 answers , now we want to send the rest of the answers excluding the above 2

        other_answers_with_descendants = []

        answers = question.answers.filter(parent=None).exclude(id__in=top2_ans)
        answers = answers.order_by('-publish')[:2]
        for answer in answers:
            # print('This is what the pending answers are - ', answer)
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
        
        return HttpResponse('yelp your question has been uploaded')

    return render(request, 'qna\create_question.html')

def minichat_view(request, *args, **kwargs):
    return render(request, "qna\qnaroom.html")


def addAnswer_view(request, *args, **kwargs):

    print('The addAnswer view is called')
    user = request.user

    if not request.user.is_authenticated:
        return redirect("login")

    if request.POST:


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
            except Answer.DoesNotExist:
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
            except Answer.DoesNotExist:
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
            except Answer.DoesNotExist:
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
                    answer = Answer(question = question, user = user, content=content)
                    answer.save()
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
