
SecondSupervisor = {
    inject: ['appraisalData', 'submitFunction', 'changeComponent'],
    data() {
        return {
            formData: {},
            disableButton: false,
            buttonText: "Validate and Submit",
            diabledFields: true
        }
    },
    watch: {
        appraisalData: {
            handler(newVal, oldVal) {
                if (newVal.value) this.writeDataToForm(newVal)
            },
            immediate: true,
            deep: true
        },
    },
    methods: {
        writeDataToForm(data) {
            this.formData['appraisal_id'] = data.value['id']
            this.formData['setting_state'] = true
            this.formData['target_state'] = this.appraisalData.value.metaInfo.next_stage
            this.formData['setting_2nd_supervisor_data'] = true
            this.formData['p8_2sup_q1'] = data.value['p8_2sup_q1']
            this.formData['p8_2sup_q1_reason'] = data.value['p8_2sup_q1_reason']
            this.formData['p8_2sup_q2'] = data.value['p8_2sup_q2']

            if (data.value.state == '2nd_supervisor_review') {
                this.diabledFields = false
            } else {
                this.diabledFields = true
            }

        },
        async submitForm() {
            if(!confirm('Are you sure?')) {
                return
            }
            this.disableButton = true
            this.buttonText = "Saving..."
            result = await this.submitFunction(this.formData)
            this.disableButton = false
            this.buttonText = "Validate and Submit"
        }   
    },
    components: {
        FullForm,
        SubmitForm
    },
    template: `
        <div>
            <div class="alert custom_alert text-center d-block">
                The employee and his supervisor have completed providing their feedback with regards to this appraisal record, and it has been forwarded to you further further review. 
                Kindly review all answers and once reviewed, use the section at the end of this page to provide your feedback and move the appraisal to the final stage.
                In case you believe feedback provided by either the employee or supervisor needs to be modified, use the button 'Move Back to supervisor Review.
            </div>
            <hr/>
            <FullForm />
            <hr/>
            <form class="form-group" @submit.prevent="submitForm" v-if="appraisalData.value.metaInfo.hasCurrentComponentAccess">
                <fieldset>
                    <label for="" class="font-weight-normal mr-2">Do you agree with the above performance appraisal of the direct line manager?</label>
                    <div class="custom-control custom-radio custom-control-inline">
                        <input type="radio" class="custom-control-input" id="question1a" name="question1" value="yes" v-model="formData.p8_2sup_q1" :disabled="diabledFields">
                        <label class="custom-control-label" for="question1a">Yes</label>
                    </div>
                    <div class="custom-control custom-radio custom-control-inline">
                        <input type="radio" class="custom-control-input" id="question1b" name="question1" value="no" v-model="formData.p8_2sup_q1" :disabled="diabledFields">
                        <label class="custom-control-label" for="question1b">No</label>
                    </div>
                    <br/>
                    <label for="" class="font-weight-normal">Comments if any:</label>
                    <textarea class="form-control" rows="3" placeholder="Comments if any..." v-model="formData.p8_2sup_q1_reason" :disabled="diabledFields"></textarea>
                </fieldset>
                <fieldset class="mt-2">
                    <label for="" class="font-weight-normal mr-2">Are you directly familiar with thisstaff member's work?</label>
                    <br/>
                    <div class="custom-control custom-radio custom-control-inline">
                        <input type="radio" class="custom-control-input" id="question2a" name="question2" value="yes" v-model="formData.p8_2sup_q2" :disabled="diabledFields">
                        <label class="custom-control-label" for="question2a">Yes, directly</label>
                    </div>
                    <div class="custom-control custom-radio custom-control-inline">
                        <input type="radio" class="custom-control-input" id="question2b" name="question2" value="no" v-model="formData.p8_2sup_q2" :disabled="diabledFields">
                        <label class="custom-control-label" for="question2b">No, only through the direct line manager.</label>
                    </div>
                    <div class="custom-control custom-radio custom-control-inline">
                        <input type="radio" class="custom-control-input" id="question2c" name="question2" value="other" v-model="formData.p8_2sup_q2" :disabled="diabledFields">
                        <label class="custom-control-label" for="question2c">Technical manager/Line Director.</label>
                    </div>
                </fieldset>
                <hr/>
                <div style="font-size: 13px">
                    <strong style="color: #5c5c5c">Note:</strong> 
                    <span class="ml-1">by choosing to click on the 'Sign' buttons above, you hereby confirm that you have provided your feedback and comments with regards to this appraisal to the best of your knowledge. This confirmation, along with the date and time of your confirmation, will be logged by the system as your electronic signature for this document.</span>
                </div>
                <button class="btn btn-secondary mt-3" v-if="appraisalData.value.metaInfo.setSubmitAccess" :disabled="disableButton">{{ buttonText }}</button>
                <button type="button" v-if="(['both_user', 'is_only_second_manager'].includes(appraisalData.value.manager_type) && appraisalData.value.state == '2nd_supervisor_review')" @click="changeComponent('AppraisalStateReturner')" class="btn btn-secondary mt-3 ml-2">
                    <i class="fa fa-view" /> 
                    Move back to Supervisor to Review
                </button>
            </form>
        </div>
    `,
}