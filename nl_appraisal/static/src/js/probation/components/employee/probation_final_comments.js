
EProbationFinalComment = {
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
        ProbationFullForm,
        ProbationSubmitForm
    },
    template: `
        <div>
            <ProbationFullForm />
            <hr/>
            <form class="form-group" @submit.prevent="submitForm">
                <div style="font-size: 13px">
                    <strong style="color: #5c5c5c">Note:</strong> 
                    <span class="ml-1">by choosing to click on the 'Sign and Submit' button above, you hereby confirm that you have reviewed your appraisal record, along with the feedback and comments provided by your supervisor(s). This confirmation, along with the date and time of your confirmation, will be logged by the system as your electronic signature for this document. This document will be logged as part of your HR file. You can always retrieve and review this document from your portal</span>
                </div>
                <button class="btn btn-secondary bt-sm mt-3 btn-odoo py-2" v-if="appraisalData.value.metaInfo.setSubmitAccess" :disabled="disableButton">{{ buttonText }}</button>
            </form>
        </div>
    `,
}