ProbationPerformanceFeedback = {
    inject: ['appraisalData', 'submitFunction', 'changeComponent', 'toggleChat'],
    data() {
        return {
            formData: {},
            disableButton: false,
            buttonText: "Save and next",
            readOnlyMode: true,
            editButtonText: "Edit"
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
        changeReadOnlyMode(changeData=true) {
            this.readOnlyMode = !this.readOnlyMode
            if (this.readOnlyMode) {
                this.editButtonText = "Edit"
                this.toggleChat('block')
                if (changeData) this.writeDataToForm(this.appraisalData)
            }else {
                this.editButtonText = "Discard"
                this.toggleChat('none')
            }
        },
        writeDataToForm(data) {
            this.formData['appraisal_id'] = data.value['id']
            this.formData['has_sup_performance'] = true
            this.formData['p3_q1'] = data.value['p3_q1']
            this.formData['p3_q2'] = data.value['p3_q2']
            this.formData['p3_q3'] = data.value['p3_q3']
            this.formData['p3_sup_comments'] = data.value['p3_sup_comments']
        },
        async submitForm() {
            this.disableButton = true
            this.buttonText = "Saving..."
            result = await this.submitFunction(this.formData)
            if (result) {
                this.changeReadOnlyMode(changeData=false)
                if (this.appraisalData.value.metaInfo.setting_performance_feedback_state){
                    this.changeComponent('ProbationWayForward')
                }
            }
            this.disableButton = false
            this.buttonText = "Save and next"
        }
    },
    template: `
        <div>
            <h3 style="font-size: 20px;background: #ffffff;padding: 10px 0;margin-top: 20px;border-bottom: 4px solid #875a7b;text-transform: uppercase;">Performance Feedback</h3>
            <div class="py-5">
                <form class="form-group" @submit.prevent="submitForm">
                    <div class="form_buttons" v-if="appraisalData.value.metaInfo.hasCurrentComponentAccess">
                        <button type="button" class="btn btn-secondary text-white" @click="changeReadOnlyMode" v-if="!disableButton">{{ editButtonText }}</button>
                        <button  class="btn btn-secondary text-white" :disabled="disableButton" v-if="!readOnlyMode">{{ buttonText }}</button>
                    </div>
                    <label class="font-weight-normal mt-5" for="p3_q1">
                        1. Highlight areas where the employee is performing well against objectives and set standards.
                    </label>
                    <textarea class="form-control disabled-textarea" rows="5" placeholder="Manager Comment..." :disabled="readOnlyMode" 
                        v-model="formData.p3_q1" name="p3_q1" id="p3_q1"></textarea>
                    <br/>
                    <label class="font-weight-normal" for="p3_q2">
                        2. Are there areas that require imporvement? (give details/ examples)
                    </label>
                    <textarea class="form-control disabled-textarea" rows="5" placeholder="Manager Comment..." :disabled="readOnlyMode" 
                    v-model="formData.p3_q2" name="p3_q2" id="p3_q2"></textarea>
                    <br/>
                    <label class="font-weight-normal" for="p3_q3">
                        3. Outline the plans for performance improvement.
                    </label>
                    <textarea class="form-control disabled-textarea" rows="5" placeholder="Manager Comment..." :disabled="readOnlyMode" 
                        v-model="formData.p3_q3" name="p3_q3" id="p3_q3"></textarea>
                    <br/>
                    <label class="font-weight-bold" for="p3_sup_comments">
                        Supervisors's summary of employee's overall performance:
                    </label>
                    <textarea class="form-control disabled-textarea" rows="5" placeholder="Manager Comment..." :disabled="readOnlyMode" 
                        v-model="formData.p3_sup_comments" name="p3_sup_comments" id="p3_sup_comments"></textarea>
            </form>
            </div>    
        </div>
    `,
}