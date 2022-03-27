PIPFullForm = {
    inject: ['appraisalData', 'changeComponent'],
    data() {
        return {
            data: {}
        }
    },
    watch: {
        appraisalData: {
            handler(newVal, oldVal) {
                if (newVal.value) this.data = newVal.value
            },
            immediate: true,
            deep: true
        },
    },
    template: `
        <div>
            <a class="btn btn-secondary btn-sm btn-odoo" :href="'/report/pdf/nl_appraisal.report_appraisal_pip/' + data.id" v-if="data.state == 'done'">
                <i class="fa fa-view" /> 
                print
            </a>
            <button v-if="(appraisalData.value.metaInfo.byManager == true && appraisalData.value.state == 'final_comments')" @click="changeComponent('PIPAppraisalStateReturner')" class="btn btn-secondary btn-sm btn-odoo">
                <i class="fa fa-view" /> 
                Move back to Assessment
            </button>
            <div class="mt-3" v-if="(appraisalData.value.metaInfo.byManager == false && appraisalData.value.state == 'final_comments')">
                Note: <span class="text-muted">
                    Your supervisor has provided their assessment notes with regards to your pertormance with respect to this performanc
                    Abasin. improvement olan. Please review their feedback below.
                    and once completed, navigate to the 'Sign and Submit' section to finalize thep process. You can use the chatter at the end of the page
                    to communicate with your supervisor regarding any issues related to this plan.
                </span>
            </div>
            <div class="mt-4 custom_font_size">
                <h3>General Information</h3>
                <div class="row bg-white mt-2">
                    <div class="col-lg-3 headr border-grey border py-1 px-2 custom_font_size" >Employee Name:</div>
                    <div class="col-lg-9 border-grey border odoo-cell-grey py-1 px-2 custom_font_size">{{ data.employee_name }}</div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-3 headr border-grey border py-1 px-2 custom_font_size">Position</div>
                    <div class="col-lg-9 border-grey border odoo-cell-grey py-1 px-2 custom_font_size">{{ data.position }}</div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-3 headr border-grey border py-1 px-2 custom_font_size">Supervisor(s)</div>
                    <div class="col-lg-9 border-grey border odoo-cell-grey py-1 px-2 custom_font_size"> {{ data.manager_name }} </div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-3 headr border-grey border py-1 px-2 custom_font_size">Date of initial Meeting</div>
                    <div class="col-lg-9 border-grey border odoo-cell-grey py-1 px-2 custom_font_size"> {{ data.initial_meeting_date }} </div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-3 headr border-grey border py-1 px-2 custom_font_size">Name(s) of other attendee (s)</div>
                    <div class="col-lg-9 border-grey border odoo-cell-grey py-1 px-2 custom_font_size"> 
                        <span v-for="atten in data.other_attendees_names ">
                            {{ atten }}, 
                        </span> 
                    </div>
                </div>
            </div>

            <div class="mt-5 custom_font_size" v-if="data.objectives">
                <div class="bg-white mt-2">
                    <div class="row">
                        <div class="col-lg-3 border-grey border py-1 px-2 headr" >
                            <div class="font-weight-bold text-center mb-1">Target Area</div>
                            <div class="d-block text-center"><small>Detail specific area where performance standards have not been met.</small></div>
                        </div>
                        <div class="col-lg-3 border-grey border py-1 px-2 headr" >
                            <div class="font-weight-bold text-center mb-1">Performance Concern</div>
                            <div class="d-block text-center"><small>Detail specific dates and examples of where the standards have not been met.</small></div>
                        </div>
                        <div class="col-lg-3 border-grey border py-1 px-2 headr" >
                            <div class="font-weight-bold text-center mb-1">Agreed Improvement Action</div>
                            <div class="d-block text-center"><small>Detail what is expected of the employee in terms of their performance i.e. what does ‘good’ look like.</small></div>
                        </div>
                        <div class="col-lg-3 border-grey border py-1 px-2 headr" >
                            <div class="font-weight-bold text-center mb-1">Support</div>
                            <div class="d-block text-center"><small>Detail what has been agreed in terms of support required to achieve the expected standard of performance</small></div>
                        </div>
                    </div>
                    <div class="row" v-for="obj in data.objectives">
                        <div class="col-lg-3 border-grey border odoo-cell-grey">{{ obj.name }}</div>
                        <div class="col-lg-3 border-grey border odoo-cell-grey">{{ obj.performance_concern }}</div>
                        <div class="col-lg-3 border-grey border odoo-cell-grey">{{ obj.agreed_improvement_action }}</div>
                        <div class="col-lg-3 border-grey border odoo-cell-grey">{{ obj.support }}</div>
                    </div>
                </div>
            </div>

            <div class="mt-5 custom_font_size" v-if="data.reviews">
                <div class="bg-white mt-2">
                    <div class="row">
                        <div class="col-lg-1 border-grey border py-1 px-2 headr" ></div>
                        <div class="col-lg-3 border-grey border py-1 px-2 headr" >
                            <div class="font-weight-bold text-center mb-1">Review Date</div>
                        </div>
                        <div class="col-lg-6 border-grey border py-1 px-2 headr" >
                            <div class="font-weight-bold text-center mb-1">Review Notes</div>
                        </div>
                        <div class="col-lg-2 border-grey border py-1 px-2 headr" >
                            <div class="font-weight-bold text-center mb-1">Creteria</div>
                        </div>
                    </div>
                    <div class="row" v-for="(obj, index) in data.reviews">
                        <div class="col-lg-1 border-grey border odoo-cell-grey">{{ index+1 }}</div>
                        <div class="col-lg-3 border-grey border odoo-cell-grey">{{ obj.review_date }}</div>
                        <div class="col-lg-6 border-grey border odoo-cell-grey">{{ obj.notes }}</div>
                        <div class="col-lg-2 border-grey border odoo-cell-grey">{{ data.creteria_dict[obj.result] }}</div>
                    </div>
                </div>
            </div>

            <div class="mt-5 custom_font_size" v-if="data.state == 'done'">
                <h5>This action has been agreed by:</h5>
                <div class="bg-white mt-2">
                    <div class="row">
                        <div class="col-lg-3 border-grey border py-1 px-2 headr border-bottom-white" >Signed by</div>
                        <div class="col-lg-3 border-grey border py-1 px-2 headr border-bottom-white" >Name</div>
                        <div class="col-lg-3 border-grey border py-1 px-2 headr border-bottom-white" >Signature</div>
                        <div class="col-lg-3 border-grey border py-1 px-2 headr border-bottom-white" >Date</div>
                    </div>
                    <div class="row">
                        <div class="col-lg-3 border-grey border  py-1 px-2 headr border-bottom-white" >Employee</div>
                        <div class="col-lg-3 border-grey border odoo-cell-grey py-1 px-2" >{{ data.employee_name }}</div>
                        <div class="col-lg-3 border-grey border odoo-cell-grey py-1 px-2" ></div>
                        <div class="col-lg-3 border-grey border odoo-cell-grey py-1 px-2" >{{ data.employee_sign_date }}</div>
                    </div>
                    <div class="row">
                        <div class="col-lg-3 border-grey border  py-1 px-2 headr border-bottom-white" >Supervisor</div>
                        <div class="col-lg-3 border-grey border odoo-cell-grey py-1 px-2" >{{ data.manager_name }}</div>
                        <div class="col-lg-3 border-grey border odoo-cell-grey py-1 px-2" ></div>
                        <div class="col-lg-3 border-grey border odoo-cell-grey py-1 px-2" >{{ data.manager_sign_date }}</div>
                    </div>
                </div>
            </div>

        </div>
    `
}