ProbationFullForm = {
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
            <a class="btn btn-secondary btn-sm btn-odoo" :href="'/report/pdf/nl_appraisal.report_proabation_appraisal/' + data.id" v-if="data.metaInfo.state == 'done'">
                <i class="fa fa-view" /> 
                print
            </a>
            <button v-if="appraisalData.value.by_managers && appraisalData.value.state == 'final_comments'" @click="changeComponent('ProbationStateReturner')" class="btn btn-secondary btn-sm btn-odoo">
                <i class="fa fa-view" /> 
                Move back to Supervisor Assessment
            </button>
            <div class="mt-4">
                <h3>General Information</h3>
                <div class="row bg-white mt-2">
                    <div class="col-lg-2 border-grey border py-1 px-2 headr custom_font_size" >Employee Name:</div>
                    <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ data.employee_name }}</div>
                    <div class="col-lg-2 border-grey border py-1 px-2 headr custom_font_size">Emp. ID No.</div>
                    <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ data.employee_idc_no }}</div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-2 border-grey border py-1 px-2 headr custom_font_size">Position Title:</div>
                    <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ data.position }}</div>
                    <div class="col-lg-2 border-grey border py-1 px-2 headr custom_font_size" >Office/Region:</div>
                    <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ data.office }}</div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-2 border-grey border py-1 px-2 headr custom_font_size">Manager Name:</div>
                    <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ data.manager_name }}</div>
                    <div class="col-lg-2 border-grey border py-1 px-2 headr custom_font_size" >Manager Position:</div>
                    <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ data.manager_position }}</div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-4 border-grey border py-1 px-2 headr custom_font_size" >Review Period:</div>
                    <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size"> {{ data.from_date }} </div>
                    <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">{{ data.to_date }}</div>
                </div>
            </div>

            <div class="mt-5">
                <h3 >Objectives set and achieved during the review period.</h3>
                <div class="row bg-white mt-2">
                    <div class="col-lg-6 border-grey border py-1 px-2 headr" >List of Objectives</div>
                    <div class="col-lg-6 border-grey border py-1 px-2 headr" >Expected Outcome</div>
                    <template v-for="obj in data.objectives">
                        <div class="col-lg-6 border-grey border py-1 px-2 custom_font_size">{{ obj.name }}</div>
                        <div class="col-lg-6 border-grey border py-1 px-2 custom_font_size">{{ obj.expected_outcome }}</div>
                    </template>
                </div>
            </div>

            <template v-if="!['objective_setting', 'probation_period', 'self_assessment'].includes(data.state)">

                <div class="mt-5">
                    <h3 >Overall Assessment</h3>
                    <div class="row bg-white mt-2">
                        <div class="col-lg-4 border-grey border py-1 px-2 headr" >Assessment Area</div>
                        <div class="col-lg-2 border-grey border py-1 px-2 headr" >Improvement required</div>
                        <div class="col-lg-2 border-grey border py-1 px-2 headr" >Average</div>
                        <div class="col-lg-2 border-grey border py-1 px-2 headr" >Good</div>
                        <div class="col-lg-2 border-grey border py-1 px-2 headr" >Excellent</div>
                    
                            <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">Quality and accuracy of work</div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q1 == 'improvement_required'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q1 == 'average'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q1 == 'good'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q1 == 'excellent'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>

                            <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">Efficiency</div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q2 == 'improvement_required'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q2 == 'average'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q2 == 'good'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q2 == 'excellent'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>

                            <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">Attendance and time keeping</div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q3 == 'improvement_required'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q3 == 'average'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q3 == 'good'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q3 == 'excellent'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>

                            <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">Understating and application of SCA policies and Values</div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q4 == 'improvement_required'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q4 == 'average'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q4 == 'good'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q4 == 'excellent'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>

                            <div class="col-lg-4 border-grey border py-1 px-2 custom_font_size">Work relationships (Teamwork, interpersonal and communication skills)</div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q5 == 'improvement_required'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q5 == 'average'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q5 == 'good'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>
                            <div class="col-lg-2 border-grey border py-1 px-2 custom_font_size text-center text-success" >
                                <svg v-if="data.p2_q5 == 'excellent'" style="width:1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </div>
                    </div>
                </div>


                <div class="mt-5">
                    <h3 >Performance Feedback</h3>
                    <div class="row bg-white mt-2">
                        <div class="col-lg-12 border-grey border py-1 px-2 headr">1. Highlight areas where the employee is performing well against objectives and set standards.</div>
                        <div class="col-lg-12 border-grey border py-1 px-2">{{data.p3_q1}}</div>
                        <div class="col-lg-12 border-grey border py-1 px-2 headr">2. Are there areas that require improvement? (give details/ examples)</div>
                        <div class="col-lg-12 border-grey border py-1 px-2">{{data.p3_q2}}</div>
                        <div class="col-lg-12 border-grey border py-1 px-2 headr">3. Outline the plans for performance improvement.</div>
                        <div class="col-lg-12 border-grey border py-1 px-2">{{data.p3_q3}}</div>
                        <div class="col-lg-12 border-grey border py-1 px-2 headr">Supervisor's summary of employee's overall performance</div>
                        <div class="col-lg-12 border-grey border py-1 px-2">{{data.p3_sup_comments}}</div>
                    
                    </div>
                </div>

                <div class="mt-5">
                    <h3>Employee's Comments</h3>
                    <div class="row bg-white mt-2">
                        <div class="col-lg-12 border-grey border py-1 px-2 headr">Employees Major Achievements:</div>
                        <div class="col-lg-12 border-grey border py-1 px-2">{{data.emp_major_achievements}}</div>
                        <div class="col-lg-12 border-grey border py-1 px-2 headr">Employees view on the job, work environment and working conditions</div>
                        <div class="col-lg-12 border-grey border py-1 px-2">{{data.p3_emp_comments}}</div>
                    </div>
                </div>

                <div class="mt-5">
                    <h3 >Way forward</h3>
                    <div class="row bg-white mt-2">
                        <div class="col-lg-5 border-grey border py-1 px-2">Is the employee's employment with SCA is confirmed?</div>
                        <div class="col-lg-7 border-grey border py-1 px-2 text-center">{{data.p4_q1 == 'yes' ? 'Yes' : data.p4_q1 == 'no' ? 'No' : ''}}</div>
                        <template v-if="data.p4_q1 == 'no'">
                            <div class="col-lg-5 border-grey border py-1 px-2">If no, give details of the performance concerns and the proposed way forward.</div>
                            <div class="col-lg-7 border-grey border py-1 px-2 text-center">{{data.p4_q2 == 'termination' ? 'Termination of Contract' : data.p4_q2 == 'improvement' ? 'Performance Improvement Plan' : ''}}</div>
                        </template>
                    </div>
                </div>

                
                <div class="mt-5" v-if="data.employee_sign_date || data.manager_sign_date ">
                    <h3>Signed by:</h3>
                    <div v-if="data.employee_sign_date">
                        <strong>Employee:</strong> {{ data.employee_name }} on {{ data.employee_sign_date }}
                    </div>
                    <div v-if="data.manager_sign_date">
                        <strong>Supervisor:</strong> {{ data.manager_name }} on {{ data.manager_sign_date }}
                    </div>
                </div>
            </template>

        </div>
    `
}