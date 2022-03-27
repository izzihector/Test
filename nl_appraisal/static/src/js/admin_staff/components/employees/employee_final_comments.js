
EFinalComment = {
    inject: ['appraisalData', 'submitFunction', 'changeComponent'],
    data() {
        return {
            formData: {},
            disableButton: false,
            buttonText: "Sign and Submit",
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
            this.formData['setting_final_comments_data'] = true
            this.formData['p9_emp_feed'] = data.value['p9_emp_feed']
            this.formData['p9_emp_feed_comments'] = data.value['p9_emp_feed_comments']

            
            
            if (data.value.state == 'final_comments') {
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
            this.buttonText = "Sign and Submit"
        }   
    },
    components: {
        FullForm,
        SubmitForm
    },
    template: `
        <div>
            <div class="alert custom_alert text-center d-block">
                Your appraisal is now complete. To finalize the process, carefully review all of the feedback provided by your supervisor(s) below, and once reviewed - 
                use the section at the end of this page to provide your consent and sign on the appraisal. If you have any issues and you would like to request that the appraisal 
                undergo further review, please contact your supervisor or HR. 
            </div>
            <hr/>
            <FullForm />
            <hr/>
            <h3>Employee’s feedback on rating and recommendations</h3>
            <form class="form-group" @submit.prevent="submitForm">
                <fieldset>
                    <label for="" class="font-weight-normal mr-2">Do you agree With the above performance appraisal rating and recommendation.?</label>
                    <div class="custom-control custom-radio custom-control-inline">
                        <input type="radio" class="custom-control-input" id="question1a" name="question1" value="yes" v-model="formData.p9_emp_feed" :disabled="diabledFields">
                        <label class="custom-control-label" for="question1a">I agree</label>
                    </div>
                    <div class="custom-control custom-radio custom-control-inline">
                        <input type="radio" class="custom-control-input" id="question1b" name="question1" value="no" v-model="formData.p9_emp_feed" :disabled="diabledFields">
                        <label class="custom-control-label" for="question1b">I do not agree</label>
                    </div>
                    <br/>
                    <label for="" class="font-weight-normal">Comments (if any):</label>
                    <textarea class="form-control" rows="3" placeholder="Comments (if any)..." v-model="formData.p9_emp_feed_comments" :disabled="diabledFields"></textarea>
                    <small class="text-muted">(I Understand that I am entitled to submit a statement of explanation if I so wish.)</small>
                </fieldset>
                <hr/>
                <div style="font-size: 13px">
                    <strong style="color: #5c5c5c">Note:</strong> 
                    <span class="ml-1">by choosing to click on the 'Sign and Submit' button below, you hereby confirm that you have reviewed your appraisal record, along with the feedback and comments provided by your supervisor(s). This confirmation, along with the date and time of your confirmation, will be logged by the system as your electronic signature for this document. This document will be logged as part of your HR file. You can always retrieve and review this document from your portal</span>
                </div>
                <button class="btn btn-secondary btn-odoo bt-sm mt-3" v-if="appraisalData.value.metaInfo.setSubmitAccess" :disabled="disableButton">{{ buttonText }}</button>
            </form>
        </div>
    `,
}