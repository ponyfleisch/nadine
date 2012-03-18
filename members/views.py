import traceback
from datetime import date, datetime, timedelta

from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required

from staff.models import Member, Transaction
from forms import EditProfileForm
from interlink.forms import MailingListSubscriptionForm
from models import HelpText

@login_required
def index(request):
	members = Member.objects.active_members().order_by('user__first_name') 
	return render_to_response('members/index.html',{ 'members':members }, context_instance=RequestContext(request))

@login_required
def profile_redirect(request):
	return HttpResponseRedirect(reverse('members.views.user', kwargs={'username':request.user.username}))

@login_required
def user(request, username):
	user = get_object_or_404(User, username=username)
	member = get_object_or_404(Member, user=user)
	return render_to_response('members/user.html',{'user':user, 'member':member}, context_instance=RequestContext(request))

@login_required
def mail(request, username):
	user = get_object_or_404(User, username=username)
	if not user == request.user: return HttpResponseRedirect(reverse('members.views.user', kwargs={'username':request.user.username}))
	if request.method == 'POST':
		sub_form = MailingListSubscriptionForm(request.POST)
		if sub_form.is_valid():
			sub_form.save(user)
			return HttpResponseRedirect(reverse('members.views.mail', kwargs={'username':user.username}))
	return render_to_response('members/mail.html',{'user':user, 'mailing_list_subscription_form':MailingListSubscriptionForm()}, context_instance=RequestContext(request))

@login_required
def edit_profile(request, username):
	user = get_object_or_404(User, username=username)
	member = user.get_profile()

	if request.method == 'POST':
		profile_form = EditProfileForm(request.POST, request.FILES)
		if profile_form.is_valid():
			profile_form.save()
			return HttpResponseRedirect(reverse('members.views.user', kwargs={'username':user.username}))
	else:
		profile_form = EditProfileForm(initial={'member_id':member.id, 'phone':member.phone, 'phone2':member.phone2,
			'address1':member.address1, 'address2':member.address2, 'city':member.city, 'state':member.state, 'zipcode':member.zipcode,
			'company_name':member.company_name, 'url_personal':member.url_personal, 'url_professional':member.url_professional, 
			'url_facebook':member.url_facebook, 'url_twitter':member.url_twitter, 'url_biznik':member.url_biznik, 
			'url_linkedin':member.url_linkedin, 'url_loosecubes':member.url_loosecubes, 'gender':member.gender, 'howHeard':member.howHeard,
			'industry':member.industry, 'neighborhood':member.neighborhood, 'has_kids':member.has_kids, 'self_employed':member.self_employed})

	return render_to_response('members/edit_profile.html',{'user':user, 'profile_form':profile_form}, context_instance=RequestContext(request))

@login_required
def receipt(request, username, id):
	user = get_object_or_404(User, username=username)
	if not user == request.user: 
		if not request.user.is_staff: return HttpResponseRedirect(reverse('members.views.user', kwargs={'username':request.user.username}))
	transaction = get_object_or_404(Transaction, id=id);
	if not user.profile == transaction.member: 
		if not request.user.is_staff: return HttpResponseRedirect(reverse('members.views.user', kwargs={'username':request.user.username}))
	bills = transaction.bills.all()
	return render_to_response('members/receipt.html',{'user':user, 'transaction':transaction, 'bills':bills}, context_instance=RequestContext(request))

def help_all(request):
	help_topics = HelpText.objects.all().order_by('title')
	return render_to_response('members/help.html',{'help_topics':help_topics}, context_instance=RequestContext(request))

def help_topic(request, id):
	topic = get_object_or_404(HelpText, id=id)
	return render_to_response('members/help_topic.html',{'topic':topic}, context_instance=RequestContext(request))

def tags(request):
	#tags = Member.tags.all()
	return render_to_response('members/tags.html',{'tags':tags}, context_instance=RequestContext(request))

def tag(request, tag):
	members = Member.objects.filter(tags__name__in=[tag])
	return render_to_response('members/tag.html',{'tag':tag, 'members':members}, context_instance=RequestContext(request))

# Copyright 2010 Office Nomads LLC (http://www.officenomads.com/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
